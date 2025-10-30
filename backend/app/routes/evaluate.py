from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime
import json

router = APIRouter()

# --- Try to import DB plumbing (Prisma) and helper create_audit
# If Prisma or the db client isn't installed / configured, we fall back to in-memory.
_db_available = False
try:
    from app.services.db_client import db, create_audit  # type: ignore
    _db_available = True
except Exception:
    # db client not available in this environment — we'll use in-memory fallback.
    _db_available = False

# In-memory audit store fallback
try:
    from app.services import audit_store  # type: ignore
except Exception:
    # Minimal fallback audit store if module not present (keeps runtime safe)
    audit_store = None  # type: ignore

# --- Models ---------------------------------------------------------------
class Condition(BaseModel):
    field: str
    op: str
    value: Any

class Rule(BaseModel):
    id: str
    name: str
    conditions: List[Condition] = Field(default_factory=list)
    actions: List[str] = Field(default_factory=list)
    active: bool = True
    priority: int = 0  # higher wins
    created_at: Optional[datetime] = None

class Expense(BaseModel):
    expense_id: str
    amount: Optional[float] = None
    category: Optional[str] = None
    working_hours: Optional[int] = None
    employee_id: Optional[str] = None
    merchant: Optional[str] = None
    submitted_at: Optional[datetime] = None

class EvalTraceItem(BaseModel):
    rule: str
    matched: bool
    reason: Optional[str] = None

class EvalResponse(BaseModel):
    matched_rules: List[str]
    winning_rule: Optional[str]
    actions: List[str]
    trace: List[EvalTraceItem]


# --- Example in-memory RULES (keeps behavior identical to original file) -
RULES: List[Rule] = [
    Rule(
        id="r1",
        name="Reject large expenses",
        conditions=[Condition(field="amount", op=">", value=5000)],
        actions=["require_approval"],
        priority=10,
        created_at=datetime.utcnow()
    ),
    Rule(
        id="r2",
        name="Flag overtime meal",
        conditions=[
            Condition(field="amount", op=">", value=200),
            Condition(field="working_hours", op=">", value=12)
        ],
        actions=["flag"],
        priority=20,
        created_at=datetime.utcnow()
    ),
    Rule(
        id="r3",
        name="Reject alcohol",
        conditions=[Condition(field="category", op="==", value="Alcohol")],
        actions=["reject"],
        priority=30,
        created_at=datetime.utcnow()
    )
]


# --- Helper: simple operator evaluation ----------------------------------
def eval_condition(cond: Condition, expense: Expense) -> bool:
    left = getattr(expense, cond.field, None)
    op = cond.op.strip()
    right = cond.value

    try:
        if op == ">":
            return left is not None and float(left) > float(right)
        if op == "<":
            return left is not None and float(left) < float(right)
        if op == ">=":
            return left is not None and float(left) >= float(right)
        if op == "<=":
            return left is not None and float(left) <= float(right)
        if op == "==":
            return left == right
        if op == "in":
            return left in right if left is not None else False
        if op == "contains":
            return isinstance(left, str) and str(right).lower() in left.lower()
    except Exception:
        # Any type/convert error => treat as non-match
        return False
    return False


# --- Core evaluation logic -----------------------------------------------
def evaluate_rules(expense: Expense, rules: List[Rule]) -> EvalResponse:
    matched: List[Rule] = []
    trace: List[EvalTraceItem] = []

    for r in rules:
        if not r.active:
            trace.append(EvalTraceItem(rule=r.id, matched=False, reason="inactive"))
            continue

        reasons: List[str] = []
        all_match = True
        for c in r.conditions:
            ok = eval_condition(c, expense)
            reasons.append(f"{c.field}{c.op}{c.value}:{ok}")
            if not ok:
                all_match = False

        trace.append(EvalTraceItem(rule=r.id, matched=all_match, reason=' && '.join(reasons)))
        if all_match:
            matched.append(r)

    if not matched:
        return EvalResponse(matched_rules=[], winning_rule=None, actions=[], trace=trace)

    # Sort by priority desc, then by number of conditions desc for specificity tie-break
    matched_sorted = sorted(matched, key=lambda x: (x.priority, len(x.conditions)), reverse=True)
    winning = matched_sorted[0]
    actions = winning.actions.copy()

    return EvalResponse(
        matched_rules=[r.id for r in matched],
        winning_rule=winning.id,
        actions=actions,
        trace=trace
    )


# --- Utility: convert DB rule record -> Rule model ------------------------
def _rule_from_db_record(r) -> Rule:
    """
    Accepts a Prisma rule record (with JSON fields 'conditions' and 'actions')
    and returns a Rule pydantic object.
    """
    try:
        conds = [Condition(**c) for c in r.conditions] if getattr(r, "conditions", None) else []
    except Exception:
        conds = []
    try:
        actions = list(r.actions) if getattr(r, "actions", None) else []
    except Exception:
        actions = []
    return Rule(
        id=r.id,
        name=r.name,
        conditions=conds,
        actions=actions,
        active=r.active,
        priority=r.priority,
        created_at=getattr(r, "createdAt", None)
    )


# --- Main endpoint: evaluate expense against rules -----------------------
@router.post("/orgs/{orgId}/policy/evaluate", response_model=EvalResponse)
async def evaluate(orgId: str, expense: Expense):
    if not expense.expense_id:
        raise HTTPException(status_code=400, detail="expense_id is required")

    rules_to_use: List[Rule] = []

    # Try to load active rules from DB; fall back to in-memory RULES on any error
    if _db_available:
        try:
            db_rules = await db.rule.find_many(where={"active": True})
            # convert to local Rule objects
            rules_to_use = [_rule_from_db_record(r) for r in db_rules]
            if not rules_to_use:
                # if DB has no rules, fallback to in-memory examples
                rules_to_use = RULES
        except Exception:
            # DB call failed (connection/migration/other) -> fallback
            rules_to_use = RULES
    else:
        rules_to_use = RULES

    # Evaluate
    result = evaluate_rules(expense, rules_to_use)

    # Persist audit: try DB first, else fallback to in-memory audit_store
    expense_dict = expense.model_dump()
    result_dict = result.model_dump()

    if _db_available:
        try:
            # create_audit should be an async helper that inserts an audit row
            await create_audit(orgId, expense_dict, result_dict, result.winning_rule)
        except Exception:
            # on any DB error, fallback to local audit store if available
            if audit_store is not None:
                try:
                    audit_store.add_audit(orgId, expense_dict, result_dict)
                except Exception:
                    pass
    else:
        if audit_store is not None:
            try:
                audit_store.add_audit(orgId, expense_dict, result_dict)
            except Exception:
                pass

    return result


# --- GET audits: return last N audits for an org --------------------------
@router.get("/orgs/{orgId}/policy/audit")
async def get_audit(orgId: str):
    """
    Return the last 10 evaluation audits for the given org.
    Uses DB if available, otherwise the in-memory audit_store.
    """
    if _db_available:
        try:
            rows = await db.audit.find_many(
                where={"orgId": orgId},
                order={"createdAt": "desc"},
                take=10
            )
            # Return raw DB rows (Prisma models are JSON serializable)
            return rows
        except Exception:
            # DB read failed -> fallback to audit_store
            pass

    # fallback path
    if audit_store is not None:
        return audit_store.get_last(10)
    return []

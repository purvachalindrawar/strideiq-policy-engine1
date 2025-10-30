from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime

router = APIRouter()

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

# --- Simple in-memory rule store (starter demo) ---------------------------
# These are example rules to allow local testing without DB.
# We will persist to DB/prisma in a following step.
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
    # Fetch the value from the expense
    left = getattr(expense, cond.field, None)
    # normalize ops and do comparisons safely
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
            # text containment
            return isinstance(left, str) and str(right).lower() in left.lower()
    except Exception:
        # If conversion failed or missing field, treat as non-match
        return False
    return False

# --- Core evaluation logic -----------------------------------------------
def evaluate_rules(expense: Expense, rules: List[Rule]) -> EvalResponse:
    matched: List[Rule] = []
    trace: List[EvalTraceItem] = []

    # Evaluate each active rule
    for r in rules:
        if not r.active:
            trace.append(EvalTraceItem(rule=r.id, matched=False, reason="inactive"))
            continue

        reasons = []
        all_match = True
        for c in r.conditions:
            ok = eval_condition(c, expense)
            reasons.append(f"{c.field}{c.op}{c.value}:{ok}")
            if not ok:
                all_match = False

        trace.append(EvalTraceItem(rule=r.id, matched=all_match, reason=' && '.join(reasons)))
        if all_match:
            matched.append(r)

    # Determine winning rule(s)
    if not matched:
        return EvalResponse(matched_rules=[], winning_rule=None, actions=[], trace=trace)

    # Sort by priority desc, then by number of conditions desc (more specific wins)
    matched_sorted = sorted(matched, key=lambda x: (x.priority, len(x.conditions)), reverse=True)

    winning = matched_sorted[0]
    # Merge actions from winning rule(s). For this prototype, pick single winning rule.
    actions = winning.actions.copy()

    return EvalResponse(
        matched_rules=[r.id for r in matched],
        winning_rule=winning.id,
        actions=actions,
        trace=trace
    )

# --- API endpoint --------------------------------------------------------
@router.post("/orgs/{orgId}/policy/evaluate", response_model=EvalResponse)
async def evaluate(orgId: str, expense: Expense):
    # Basic validation: ensure expense_id present
    if not expense.expense_id:
        raise HTTPException(status_code=400, detail="expense_id is required")

    # Run evaluation against in-memory rules (DB hooks later)
    resp = evaluate_rules(expense, RULES)
    # NOTE: persist audit log in DB in a follow-up step
    return resp

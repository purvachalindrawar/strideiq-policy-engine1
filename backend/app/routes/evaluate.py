from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime

router = APIRouter()

# --- Models ---------------
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
    priority: int = 0  
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

# --- Helper: simple operator evaluation ----------------------
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

    if not matched:
        return EvalResponse(matched_rules=[], winning_rule=None, actions=[], trace=trace)

    
    matched_sorted = sorted(matched, key=lambda x: (x.priority, len(x.conditions)), reverse=True)

    winning = matched_sorted[0]
    
    actions = winning.actions.copy()

    return EvalResponse(
        matched_rules=[r.id for r in matched],
        winning_rule=winning.id,
        actions=actions,
        trace=trace
    )


@router.post("/orgs/{orgId}/policy/evaluate", response_model=EvalResponse)
async def evaluate(orgId: str, expense: Expense):
    
    if not expense.expense_id:
        raise HTTPException(status_code=400, detail="expense_id is required")

    
    resp = evaluate_rules(expense, RULES)
    # NOTE: persist audit log in DB in a follow-up step
    return resp

from app.services import audit_store
router.get('/orgs/{orgId}/policy/audit')
async def get_audit(orgId: str):\
    return audit_store.get_last(10)
import json
old_evaluate = evaluate
async def evaluate(orgId: str, expense: Expense):
    if not expense.expense_id:
        raise HTTPException(status_code=400, detail='expense_id is required')
    result = evaluate_rules(expense, RULES)
    audit_store.add_audit(orgId, json.loads(expense.model_dump_json()), json.loads(result.model_dump_json()))
    return result

# --- Additional endpoint: get last N audits ----------------------------------
from app.services import audit_store

@router.get("/orgs/{orgId}/policy/audit")
async def get_audit(orgId: str):
    """Return the last 10 evaluation audits for the given org."""
    return audit_store.get_last(10)
from app.services import audit_store

# GET /orgs/{orgId}/policy/audit
@router.get("/orgs/{orgId}/policy/audit")
async def get_audit(orgId: str):
    """Return the last 10 evaluation audits for the given org."""
    return audit_store.get_last(10)

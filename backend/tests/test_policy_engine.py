import pytest
from app.routes.evaluate import evaluate_rules, Rule, Condition
from app.routes.evaluate import Expense

def test_single_rule_match():
    """Should match one rule when expense satisfies a single condition."""
    rule = Rule(
        id="r1",
        name="Over 1000 flag",
        conditions=[Condition(field="amount", op=">", value=1000)],
        actions=["flag"],
        priority=1
    )
    expense = Expense(expense_id="e1", amount=1500)
    result = evaluate_rules(expense, [rule])
    assert result.matched_rules == ["r1"]
    assert result.winning_rule == "r1"
    assert result.actions == ["flag"]

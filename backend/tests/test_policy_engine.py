import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
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
def test_no_rule_match():
    """Should return no matches when expense violates no rules."""
    from app.routes.evaluate import evaluate_rules, Rule, Condition, Expense
    rules = [
        Rule(id='r1', name='Reject > 5000', conditions=[Condition(field='amount', op='>', value=5000)], actions=['reject'], priority=1)
    ]
    expense = Expense(expense_id='e2', amount=100)
    result = evaluate_rules(expense, rules)
    assert result.matched_rules == []
    assert result.winning_rule is None
    assert result.actions == []
def test_no_rule_match():
    """Should return no matches when expense violates no rules."""
    from app.routes.evaluate import evaluate_rules, Rule, Condition, Expense
    rules = [
        Rule(id="r1", name="Reject > 5000", conditions=[Condition(field="amount", op=">", value=5000)], actions=["reject"], priority=1)
    ]
    expense = Expense(expense_id="e2", amount=100)
    result = evaluate_rules(expense, rules)
    assert result.matched_rules == []
    assert result.winning_rule is None
    assert result.actions == []
def test_multiple_rule_conflict_priority():
    """Should choose the higher priority rule when multiple match."""
    from app.routes.evaluate import evaluate_rules, Rule, Condition, Expense
    rules = [
        Rule(
            id="r1",
            name="Flag >200",
            conditions=[Condition(field="amount", op=">", value=200)],
            actions=["flag"],
            priority=5
        ),
        Rule(
            id="r2",
            name="Require approval >200",
            conditions=[Condition(field="amount", op=">", value=200)],
            actions=["require_approval"],
            priority=10
        )
    ]
    expense = Expense(expense_id="e3", amount=350)
    result = evaluate_rules(expense, rules)
    assert set(result.matched_rules) == {"r1", "r2"}
    assert result.winning_rule == "r2"  # higher priority wins
    assert result.actions == ["require_approval"]
def test_rule_ordering_effect_specificity():
    """Should prefer the rule with more specific conditions when priorities are equal."""
    from app.routes.evaluate import evaluate_rules, Rule, Condition, Expense
    rules = [
        Rule(
            id="r1",
            name="Flag over 100",
            conditions=[Condition(field="amount", op=">", value=100)],
            actions=["flag"],
            priority=5
        ),
        Rule(
            id="r2",
            name="Flag overtime meal",
            conditions=[
                Condition(field="amount", op=">", value=100),
                Condition(field="working_hours", op=">", value=12)
            ],
            actions=["flag_overtime"],
            priority=5  # same priority as r1
        )
    ]
    expense = Expense(expense_id="e4", amount=150, working_hours=13)
    result = evaluate_rules(expense, rules)
    assert set(result.matched_rules) == {"r1", "r2"}
    assert result.winning_rule == "r2"  # more conditions = more specific
    assert result.actions == ["flag_overtime"]
def test_boundary_missing_field():
    """Should handle missing required fields without crashing."""
    import pytest
    from app.routes.evaluate import evaluate_rules, Rule, Condition, Expense

    rules = [
        Rule(
            id="r1",
            name="Reject missing amount",
            conditions=[Condition(field="amount", op=">", value=100)],
            actions=["reject"],
            priority=1
        )
    ]

    # Missing 'amount' field should simply return no match
    expense = Expense(expense_id="e5")  # no amount provided
    result = evaluate_rules(expense, rules)

    assert result.matched_rules == []
    assert result.winning_rule is None
    assert result.actions == []

# backend/tests/test_db_integration.py
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from prisma import Prisma


@pytest.mark.asyncio
async def test_evaluate_and_audit_flow():
    """
    Integration test to verify evaluate + audit persistence.
    """

    # ✅ Updated client initialization for new HTTPX
    transport = ASGITransport(app=app)
    client = AsyncClient(transport=transport, base_url="http://test")

    # Ensure DB rules exist
    db = Prisma()
    await db.connect()
    rules = await db.rule.find_many()
    await db.disconnect()
    assert len(rules) >= 1, "Expected seeded rules in DB"

    # --- Run evaluation ---
    expense = {
        "expense_id": "exp_integ_test",
        "amount": 350,
        "category": "Food",
        "working_hours": 13,
        "employee_id": "user_101",
    }

    response = await client.post(f"/orgs/org123/policy/evaluate", json=expense)
    assert response.status_code == 200
    data = response.json()

    assert "winning_rule" in data
    assert data["actions"], "Expected at least one action"

    # --- Fetch audits ---
    audits_response = await client.get(f"/orgs/org123/policy/audit")
    assert audits_response.status_code == 200
    audits = audits_response.json()
    assert isinstance(audits, list)
    assert len(audits) > 0, "Expected audit entry created"

    await client.aclose()

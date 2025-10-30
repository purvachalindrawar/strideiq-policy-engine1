"""
backend/app/services/db_client.py

Prisma database service layer for the StrideIQ Policy Engine.
Handles DB connection lifecycle and provides helper functions
for accessing and persisting rules and audit records.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
from prisma import Prisma



# --- Prisma client instance ----------------------------------------------
db = Prisma()


# --- Connection lifecycle -------------------------------------------------
async def init_db() -> None:
    """Connect Prisma client to the database (called on FastAPI startup)."""
    try:
        await db.connect()
        print("✅ Connected to Prisma database.")
    except Exception as e:
        print(f"⚠️  Failed to connect Prisma DB: {e}")


async def close_db() -> None:
    """Disconnect Prisma client (called on FastAPI shutdown)."""
    try:
        await db.disconnect()
        print("🛑 Disconnected Prisma database.")
    except Exception as e:
        print(f"⚠️  Failed to disconnect Prisma DB: {e}")


# --- Rule helpers ---------------------------------------------------------
async def get_rules(org_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Fetch all active rules.
    The org_id is reserved for multi-org filtering (future extension).
    """
    try:
        rules = await db.rule.find_many(where={"active": True})
        return rules
    except Exception as e:
        print(f"⚠️  Error fetching rules: {e}")
        return []


# --- Audit helpers --------------------------------------------------------
async def create_audit(
    org_id: str,
    expense: Dict[str, Any],
    result: Dict[str, Any],
    rule_id: Optional[str] = None,
) -> None:
    """
    Insert a new audit record in the DB.
    Falls back gracefully if DB unavailable.
    """
    try:
        await db.audit.create(
            data={
                "orgId": org_id,
                "expenseJson": expense,
                "resultJson": result,
                "createdAt": datetime.utcnow(),
                "ruleId": rule_id,
            }
        )
        print(f"📝 Audit persisted for org {org_id}")
    except Exception as e:
        print(f"⚠️  Failed to persist audit: {e}")


async def get_recent_audits(org_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Return the most recent audit entries for a given org."""
    try:
        audits = await db.audit.find_many(
            where={"orgId": org_id},
            order={"createdAt": "desc"},
            take=limit,
        )
        return audits
    except Exception as e:
        print(f"⚠️  Error fetching audits: {e}")
        return []

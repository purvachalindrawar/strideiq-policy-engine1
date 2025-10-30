# backend/app/services/db_client.py
import asyncio
import json
from datetime import datetime
from prisma import Prisma

# Global Prisma client instance
db = Prisma()


async def init_db():
    """Connect Prisma client on startup."""
    if not db.is_connected():
        await db.connect()
        print("✅ Connected to Prisma database.")


async def close_db():
    """Disconnect Prisma client on shutdown."""
    if db.is_connected():
        await db.disconnect()
        print("🛑 Disconnected Prisma database.")


async def add_audit(org_id: str, expense: dict, result: dict):
    """Store evaluation audit in DB."""
    try:
        if not db.is_connected():
            await db.connect()

        await db.audit.create(
            data={
                "orgId": org_id,
                "expenseJson": json.dumps(expense),
                "resultJson": json.dumps(result),
                "createdAt": datetime.utcnow(),
            }
        )
    except Exception as e:
        print(f"⚠️  Failed to persist audit: {e}")


async def get_last_audits(limit: int = 10):
    """Retrieve last N audits."""
    if not db.is_connected():
        await db.connect()

    return await db.audit.find_many(order={"createdAt": "desc"}, take=limit)

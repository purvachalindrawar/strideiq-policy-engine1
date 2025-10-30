# backend/prisma/seed.py
"""
Seed script for the StrideIQ Policy Engine.
Inserts a few example rules into the database if none exist.
Run once after Prisma & Postgres setup:
    python prisma/seed.py
"""

from prisma import Prisma
import asyncio
import json


async def seed():
    db = Prisma()
    await db.connect()

    existing_rules = await db.rule.find_many()
    if existing_rules:
        print(f"✅ {len(existing_rules)} rule(s) already present, skipping seeding.")
        await db.disconnect()
        return

    print("🌱 No rules found — inserting default sample rules...")

    sample_rules = [
        {
            "name": "Reject large expenses",
            "conditions": json.dumps([{"field": "amount", "op": ">", "value": 5000}]),
            "actions": json.dumps(["require_approval"]),
            "active": True,
            "priority": 10,
        },
        {
            "name": "Flag overtime meal",
            "conditions": json.dumps([
                {"field": "amount", "op": ">", "value": 200},
                {"field": "working_hours", "op": ">", "value": 12}
            ]),
            "actions": json.dumps(["flag"]),
            "active": True,
            "priority": 20,
        },
        {
            "name": "Reject alcohol",
            "conditions": json.dumps([{"field": "category", "op": "==", "value": "Alcohol"}]),
            "actions": json.dumps(["reject"]),
            "active": True,
            "priority": 30,
        },
    ]

    for rule in sample_rules:
        await db.rule.create(data=rule)

    print("✅ Seeded example rules successfully.")
    await db.disconnect()


if __name__ == "__main__":
    asyncio.run(seed())

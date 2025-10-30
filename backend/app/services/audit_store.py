from typing import List, Dict, Any
from datetime import datetime

# Simple in-memory audit log for local testing.
# Each entry: { timestamp, org_id, expense, result }
AUDIT_LOG: List[Dict[str, Any]] = []

def add_audit(org_id: str, expense: Dict[str, Any], result: Dict[str, Any]) -> None:
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "org_id": org_id,
        "expense": expense,
        "result": result
    }
    # insert newest at front
    AUDIT_LOG.insert(0, entry)
    # keep log bounded to 50 entries to avoid unbounded memory use
    if len(AUDIT_LOG) > 50:
        AUDIT_LOG.pop()

def get_last(n: int = 10) -> List[Dict[str, Any]]:
    return AUDIT_LOG[:n]

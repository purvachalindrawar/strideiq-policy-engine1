# backend/app/services/audit_store.py
from typing import List, Dict, Any
from datetime import datetime
import threading

_lock = threading.Lock()

# each audit is a dict like:
# { "id": "<generated>", "orgId": "...", "expenseJson": "...", "resultJson": "...", "createdAt": "..." }
_AUDITS: List[Dict[str, Any]] = []

def _make_id() -> str:
    # short unique id for demo
    return f"aud_{int(datetime.utcnow().timestamp() * 1000)}"

def add_audit(orgId: str, expense_json: Dict[str, Any], result_json: Dict[str, Any]) -> Dict[str, Any]:
    """Add an audit entry (expense/result are plain dicts)."""
    entry = {
        "id": _make_id(),
        "orgId": orgId,
        "expenseJson": expense_json,
        "resultJson": result_json,
        "createdAt": datetime.utcnow().isoformat() + "Z",
    }
    with _lock:
        _AUDITS.insert(0, entry)  # newest first
        # keep only last 200 for demo safety
        if len(_AUDITS) > 200:
            _AUDITS[:] = _AUDITS[:200]
    return entry

def get_last(n: int = 10) -> List[Dict[str, Any]]:
    with _lock:
        return _AUDITS[:n]

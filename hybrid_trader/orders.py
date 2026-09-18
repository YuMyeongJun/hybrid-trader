"""Conservative submission receipts, separate from reconciled executions.

A broker acknowledgement (even one labelled filled) is not a fill ledger.
Consumers must reconcile executions and costs before publishing trading P&L.
"""

from dataclasses import dataclass
from typing import Any, Optional


@dataclass(frozen=True)
class OrderReceipt:
    order_id: Optional[str]
    status: str
    broker_status: Optional[str] = None


def submission_receipt(response: Any) -> OrderReceipt:
    """Never infer execution from a missing response or generic success flag."""
    if not isinstance(response, dict):
        return OrderReceipt(None, "UNKNOWN")
    if response.get("status") in {"DRY_RUN", "NOT_SENT"}:
        return OrderReceipt(None, response["status"])
    order_id = response.get("order_id") or response.get("uuid") or response.get("id")
    if not isinstance(order_id, str) or not order_id.strip():
        order_id = None
    raw_status = response.get("state", response.get("status"))
    broker_status = raw_status.lower() if isinstance(raw_status, str) else None
    if response.get("error") or broker_status in {"rejected", "failed"}:
        return OrderReceipt(order_id, "REJECTED", broker_status)
    # Cancellation and apparent completion can include partial executions.
    # Keep them unreconciled until the actual fills and fees have been loaded.
    known_states = {
        "pending", "wait", "watch", "new", "accepted", "submitted",
        "partially_filled", "filled", "done", "cancel", "cancelled",
        "canceled", "expired", "pending_new", "pending_cancel",
    }
    if order_id and broker_status in known_states:
        return OrderReceipt(order_id, "UNRECONCILED", broker_status)
    return OrderReceipt(order_id, "UNKNOWN", broker_status)

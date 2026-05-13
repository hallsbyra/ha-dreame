"""Queue snapshot helpers for HA Dreame runtime surfaces."""

from __future__ import annotations

from typing import Any

from .const import (
    ATTR_ITEM_ID,
    ATTR_OVERRIDES,
    ATTR_RESULT,
    ATTR_STATUS,
    CONF_ROOM_ID,
    CONF_ROOM_NAME,
)
from .queue_core import QueueState


def queue_item_snapshots(queue_state: QueueState) -> list[dict[str, Any]]:
    """Return queue items as Home Assistant-safe attribute dictionaries."""
    return [
        {
            ATTR_ITEM_ID: item.item_id,
            ATTR_OVERRIDES: dict(item.overrides),
            ATTR_RESULT: item.result,
            ATTR_STATUS: item.status,
            CONF_ROOM_ID: item.room_id,
            CONF_ROOM_NAME: item.room_name,
        }
        for item in queue_state.items
    ]


def count_queue_items(queue_state: QueueState, status: str) -> int:
    """Count queue items with one status."""
    return sum(item.status == status for item in queue_state.items)

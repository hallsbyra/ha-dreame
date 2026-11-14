"""Home Assistant independent runtime state models for HA Dreame."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class QueueRunTracking:
    """Runtime reconciliation metadata for one dispatched queue item."""

    run_id: str
    current_item_id: str
    last_command_at: datetime
    dispatch_retry_count: int = 0
    active_room_confirmed_since_dispatch: bool = False
    task_status_cleared_since_dispatch: bool = False
    post_run_maintenance_seen: bool = False

"""Home Assistant independent runtime state models for HA Dreame."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class QueueRunTracking:
    """Runtime reconciliation metadata for one dispatched queue item."""

    run_id: str
    current_item_id: str
    last_command_at: str
    dispatch_retry_count: int = 0
    active_room_confirmed_since_dispatch: bool = False
    task_status_cleared_since_dispatch: bool = False
    active_room_mismatch_streak: int = 0
    post_run_maintenance_seen: bool = False

"""Pure queue core for HA Dreame orchestration."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any
from uuid import uuid4


class QueueError(Exception):
    """Base queue domain exception."""


class InvalidOperation(QueueError):
    """Raised when a state transition or command is invalid."""


class ItemNotFound(QueueError):
    """Raised when a queue item does not exist."""


@dataclass(frozen=True)
class QueueItem:
    """One room in the queue."""

    item_id: str
    room_id: int
    room_name: str
    status: str = "pending"
    overrides: dict[str, Any] = field(default_factory=dict)
    result: str | None = None


@dataclass(frozen=True)
class QueueState:
    """Current queue state."""

    run_state: str = "idle"
    run_id: str | None = None
    items: tuple[QueueItem, ...] = ()
    current_item_id: str | None = None


@dataclass(frozen=True)
class ReconcileDecision:
    """One deterministic reconciliation decision."""

    complete_current_room: bool = False
    retry_current_room: bool = False
    resume_current_room: bool = False
    mark_out_of_sync_reason: str | None = None
    set_task_status_cleared_since_dispatch: bool = False
    reset_dispatch_retry_count: bool = False
    event_reasons: tuple[str, ...] = ()


TERMINAL_ITEM_STATUSES = {"completed", "skipped"}
TERMINAL_RUN_STATES = {"completed", "canceled", "out_of_sync", "blocked"}
MOP_MAINTENANCE_TASK_STATUSES = {
    "returning_to_remove_mop",
    "returning_to_install_mop",
}


def new_state() -> QueueState:
    """Create an empty queue state."""
    return QueueState()


def terminal_run_state_for_reason(reason: str) -> str:
    """Map a takeover reason to the terminal queue run state."""
    normalized_reason = str(reason or "").strip().lower()
    if normalized_reason.startswith("vacuum_route_error:"):
        return "blocked"
    return "out_of_sync"


def add_room(
    state: QueueState,
    *,
    room_id: int,
    room_name: str,
    overrides: dict[str, Any] | None = None,
) -> QueueState:
    """Append one pending room to the queue."""
    if state.run_state in TERMINAL_RUN_STATES:
        state = QueueState()

    item = QueueItem(
        item_id=uuid4().hex,
        room_id=room_id,
        room_name=room_name,
        overrides=dict(overrides or {}),
    )
    return replace(state, items=(*state.items, item))


def remove_item(state: QueueState, *, item_id: str) -> QueueState:
    """Remove one pending queue item."""
    items = list(state.items)
    item_index = _find_index_by_id(items, item_id)
    item = items[item_index]

    if state.run_state == "running" and item.status == "running":
        raise InvalidOperation("Cannot remove currently running room")
    if item.status != "pending":
        raise InvalidOperation("Only pending rooms can be removed")

    del items[item_index]
    return replace(state, items=tuple(items))


def move_item(state: QueueState, *, item_id: str, new_position: int) -> QueueState:
    """Move one pending queue item to a new zero-based position."""
    items = list(state.items)
    item_index = _find_index_by_id(items, item_id)
    item = items[item_index]

    if new_position < 0 or new_position >= len(items):
        raise InvalidOperation("new_position is out of range")

    if state.run_state == "running":
        running_index = _find_running_index(items)
        if running_index is None:
            raise InvalidOperation("Queue is running but no running room is set")
        if item.status != "pending":
            raise InvalidOperation("Only pending rooms can be moved while queue is running")
        if new_position <= running_index:
            raise InvalidOperation("Cannot move pending room before current running room")

    moved_item = items.pop(item_index)
    items.insert(new_position, moved_item)
    return replace(state, items=tuple(items))


def update_item_overrides(
    state: QueueState, *, item_id: str, overrides: dict[str, Any]
) -> QueueState:
    """Replace cleaning overrides for one pending queue item."""
    items = list(state.items)
    item_index = _find_index_by_id(items, item_id)
    item = items[item_index]

    if item.status == "running":
        raise InvalidOperation("Cannot modify overrides for currently running room")
    if item.status != "pending":
        raise InvalidOperation("Only pending rooms can be modified")

    items[item_index] = replace(item, overrides=dict(overrides))
    return replace(state, items=tuple(items))


def clear_pending(state: QueueState) -> QueueState:
    """Clear pending queue items."""
    items = [item for item in state.items if item.status != "pending"]

    if state.run_state == "running":
        if _find_running_index(items) is None:
            return new_state()
        return replace(state, items=tuple(items))

    return new_state()


def start_run(state: QueueState) -> QueueState:
    """Start queue execution from the first pending room."""
    if state.run_state == "running":
        raise InvalidOperation("Queue is already running")
    if not state.items:
        raise InvalidOperation("Queue is empty")

    items = list(state.items)
    first_pending_index = _find_first_pending_index(items)
    if first_pending_index is None:
        raise InvalidOperation("No pending rooms to start")

    first_item = items[first_pending_index]
    items[first_pending_index] = replace(first_item, status="running")
    return replace(
        state,
        run_state="running",
        run_id=uuid4().hex,
        items=tuple(items),
        current_item_id=first_item.item_id,
    )


def complete_current_room(state: QueueState) -> QueueState:
    """Complete the current room and advance to the next pending room."""
    return _finish_current_room(state, next_status="completed")


def skip_current_room(state: QueueState, *, reason: str = "skipped_by_user") -> QueueState:
    """Skip the current room and advance to the next pending room."""
    return _finish_current_room(state, next_status="skipped", result=reason)


def cancel_run(state: QueueState, *, reason: str = "canceled_by_user") -> QueueState:
    """Cancel all non-terminal queue items."""
    return replace(
        state,
        run_state="canceled",
        items=_mark_non_terminal_items(state.items, reason=reason),
        current_item_id=None,
    )


def external_takeover(
    state: QueueState,
    *,
    reason: str,
    terminal_state: str | None = None,
) -> QueueState:
    """Mark the queue as externally taken over by app or robot state."""
    return replace(
        state,
        run_state=terminal_state or terminal_run_state_for_reason(reason),
        items=_mark_non_terminal_items(state.items, reason=reason),
        current_item_id=None,
    )


def current_item(state: QueueState) -> QueueItem | None:
    """Return the current running queue item."""
    if state.current_item_id is None:
        return None
    for item in state.items:
        if item.item_id == state.current_item_id:
            return item
    return None


def evaluate_reconcile_tick(
    *,
    vacuum_state: str,
    task_status: str,
    awaiting_completion_event: bool,
    seconds_since_last_command: float | None,
    task_status_cleared_since_dispatch: bool,
    dispatch_retry_count: int,
    expected_room_id: int | None,
    observed_room_id: int | None,
    is_dock_prep_state: bool,
    active_states: set[str],
    dispatch_retry_interval_sec: int,
    dispatch_retry_max: int,
    vacuum_error_code: str = "",
    is_dock_prep_paused: bool = False,
    force_retry_after_recovery: bool = False,
    non_fatal_error_codes: set[str] | None = None,
    pause_waiting_seen: bool = False,
    is_returning_state: bool = False,
    expected_room_name: str | None = None,
    observed_room_name: str | None = None,
    cleaning_progress: int | None = None,
    active_room_mismatch_streak: int = 0,
    active_room_mismatch_required_streak: int = 1,
    active_room_mismatch_min_progress: int = 1,
    active_room_mismatch_max_progress: int | None = None,
    dock_prep_resume_ready: bool = False,
    is_mop_maintenance_state: bool = False,
) -> ReconcileDecision:
    """Evaluate one robot/queue reconciliation tick."""
    if not awaiting_completion_event:
        return ReconcileDecision()

    normalized_vacuum = (vacuum_state or "").lower()
    normalized_task = (task_status or "").lower()
    normalized_error = (vacuum_error_code or "").lower()
    normalized_expected_room_name = (expected_room_name or "").strip().lower()
    normalized_observed_room_name = (observed_room_name or "").strip().lower()
    normalized_non_fatal_errors = {
        str(code).lower() for code in (non_fatal_error_codes or set()) if str(code).strip()
    }

    event_reasons: list[str] = []
    set_task_status_cleared_since_dispatch = False
    effective_task_status_cleared = bool(task_status_cleared_since_dispatch)

    if normalized_task not in {"", "unknown", "unavailable", "completed"}:
        if not effective_task_status_cleared:
            set_task_status_cleared_since_dispatch = True
            effective_task_status_cleared = True
            event_reasons.append("task_status_cleared_after_dispatch")

    if normalized_vacuum == "error":
        if normalized_error == "route":
            return ReconcileDecision(
                mark_out_of_sync_reason=(
                    f"vacuum_route_error:expected_{expected_room_id}:observed_{observed_room_id}"
                ),
                set_task_status_cleared_since_dispatch=set_task_status_cleared_since_dispatch,
                event_reasons=tuple(event_reasons + ["vacuum_error_route_blocked"]),
            )
        if normalized_task == "completed":
            if not effective_task_status_cleared:
                event_reasons.append("task_status_completed_ignored_not_cleared_after_dispatch")
            elif normalized_error in {"", "unknown", "unavailable", "no_error"}:
                event_reasons.append("task_status_completed_ignored_due_vacuum_error")
            else:
                event_reasons.append(
                    f"task_status_completed_ignored_due_vacuum_error:{normalized_error}"
                )

        return ReconcileDecision(
            set_task_status_cleared_since_dispatch=set_task_status_cleared_since_dispatch,
            reset_dispatch_retry_count=True,
            event_reasons=tuple(
                event_reasons
                + [_vacuum_error_wait_reason(normalized_error, normalized_non_fatal_errors)]
            ),
        )

    if normalized_task == "completed":
        if not effective_task_status_cleared:
            event_reasons.append("task_status_completed_ignored_not_cleared_after_dispatch")
        else:
            if pause_waiting_seen and is_returning_state:
                return ReconcileDecision(
                    mark_out_of_sync_reason="manual_return_to_dock_after_pause",
                    set_task_status_cleared_since_dispatch=set_task_status_cleared_since_dispatch,
                    event_reasons=tuple(
                        event_reasons + ["task_status_completed_after_manual_pause_returning"]
                    ),
                )
            return ReconcileDecision(
                complete_current_room=True,
                set_task_status_cleared_since_dispatch=set_task_status_cleared_since_dispatch,
                event_reasons=tuple(event_reasons + ["task_status_completed"]),
            )

    if normalized_task in MOP_MAINTENANCE_TASK_STATUSES or is_mop_maintenance_state:
        if normalized_error not in {"", "unknown", "unavailable", "no_error"}:
            return ReconcileDecision(
                set_task_status_cleared_since_dispatch=set_task_status_cleared_since_dispatch,
                reset_dispatch_retry_count=True,
                event_reasons=tuple(
                    event_reasons
                    + [_vacuum_error_wait_reason(normalized_error, normalized_non_fatal_errors)]
                ),
            )
        return ReconcileDecision(
            set_task_status_cleared_since_dispatch=set_task_status_cleared_since_dispatch,
            event_reasons=tuple(event_reasons + ["mop_maintenance_waiting"]),
        )

    if is_dock_prep_state and is_dock_prep_paused and not normalized_task.endswith("_paused"):
        if normalized_error not in {"", "unknown", "unavailable", "no_error"}:
            return ReconcileDecision(
                set_task_status_cleared_since_dispatch=set_task_status_cleared_since_dispatch,
                reset_dispatch_retry_count=True,
                event_reasons=tuple(
                    event_reasons
                    + [_vacuum_error_wait_reason(normalized_error, normalized_non_fatal_errors)]
                ),
            )
        if (
            dock_prep_resume_ready
            and seconds_since_last_command is not None
            and seconds_since_last_command >= dispatch_retry_interval_sec
        ):
            return ReconcileDecision(
                resume_current_room=True,
                set_task_status_cleared_since_dispatch=set_task_status_cleared_since_dispatch,
                event_reasons=tuple(event_reasons + ["dock_prep_paused_resume_requested"]),
            )
        wait_reason = (
            "dock_prep_paused_waiting_retry_interval"
            if dock_prep_resume_ready
            else "dock_prep_paused_waiting_resume_ready"
        )
        return ReconcileDecision(
            set_task_status_cleared_since_dispatch=set_task_status_cleared_since_dispatch,
            event_reasons=tuple(event_reasons + [wait_reason]),
        )

    is_paused_state = normalized_vacuum == "paused" or normalized_task.endswith("_paused")
    if is_paused_state:
        if normalized_error not in {"", "unknown", "unavailable", "no_error"}:
            return ReconcileDecision(
                set_task_status_cleared_since_dispatch=set_task_status_cleared_since_dispatch,
                reset_dispatch_retry_count=True,
                event_reasons=tuple(
                    event_reasons
                    + [_vacuum_error_wait_reason(normalized_error, normalized_non_fatal_errors)]
                ),
            )
        return ReconcileDecision(
            set_task_status_cleared_since_dispatch=set_task_status_cleared_since_dispatch,
            event_reasons=tuple(event_reasons + ["vacuum_paused_waiting"]),
        )

    normalized_active_states = {state.lower() for state in active_states}
    desired_in_progress = normalized_vacuum in normalized_active_states or is_dock_prep_state
    if desired_in_progress:
        return _evaluate_active_reconcile(
            event_reasons=event_reasons,
            set_task_status_cleared_since_dispatch=set_task_status_cleared_since_dispatch,
            normalized_vacuum=normalized_vacuum,
            is_dock_prep_state=is_dock_prep_state,
            expected_room_id=expected_room_id,
            observed_room_id=observed_room_id,
            normalized_expected_room_name=normalized_expected_room_name,
            normalized_observed_room_name=normalized_observed_room_name,
            cleaning_progress=cleaning_progress,
            active_room_mismatch_streak=active_room_mismatch_streak,
            active_room_mismatch_required_streak=active_room_mismatch_required_streak,
            active_room_mismatch_min_progress=active_room_mismatch_min_progress,
            active_room_mismatch_max_progress=active_room_mismatch_max_progress,
            seconds_since_last_command=seconds_since_last_command,
            dispatch_retry_interval_sec=dispatch_retry_interval_sec,
            dispatch_retry_count=dispatch_retry_count,
        )

    if force_retry_after_recovery:
        return ReconcileDecision(
            retry_current_room=True,
            set_task_status_cleared_since_dispatch=set_task_status_cleared_since_dispatch,
            event_reasons=tuple(event_reasons + ["retry_dispatch_after_error_recovery"]),
        )

    if dispatch_retry_count >= dispatch_retry_max:
        return ReconcileDecision(
            mark_out_of_sync_reason=(
                f"dispatch_retry_exhausted:expected_{expected_room_id}:"
                f"observed_{observed_room_id}:vacuum_{normalized_vacuum}"
            ),
            set_task_status_cleared_since_dispatch=set_task_status_cleared_since_dispatch,
            event_reasons=tuple(event_reasons + ["dispatch_retry_exhausted"]),
        )

    if (
        seconds_since_last_command is not None
        and seconds_since_last_command >= dispatch_retry_interval_sec
    ):
        return ReconcileDecision(
            retry_current_room=True,
            set_task_status_cleared_since_dispatch=set_task_status_cleared_since_dispatch,
            event_reasons=tuple(
                event_reasons + [f"retry_dispatch_requested:{dispatch_retry_count + 1}"]
            ),
        )

    return ReconcileDecision(
        set_task_status_cleared_since_dispatch=set_task_status_cleared_since_dispatch,
        event_reasons=tuple(event_reasons),
    )


def _vacuum_error_wait_reason(normalized_error: str, normalized_non_fatal_errors: set[str]) -> str:
    if normalized_error in normalized_non_fatal_errors:
        return f"vacuum_error_non_fatal:{normalized_error}"
    return "vacuum_error_waiting_user_action"


def _evaluate_active_reconcile(
    *,
    event_reasons: list[str],
    set_task_status_cleared_since_dispatch: bool,
    normalized_vacuum: str,
    is_dock_prep_state: bool,
    expected_room_id: int | None,
    observed_room_id: int | None,
    normalized_expected_room_name: str,
    normalized_observed_room_name: str,
    cleaning_progress: int | None,
    active_room_mismatch_streak: int,
    active_room_mismatch_required_streak: int,
    active_room_mismatch_min_progress: int,
    active_room_mismatch_max_progress: int | None,
    seconds_since_last_command: float | None,
    dispatch_retry_interval_sec: int,
    dispatch_retry_count: int,
) -> ReconcileDecision:
    room_mismatch = False
    if normalized_vacuum == "cleaning" and not is_dock_prep_state:
        if normalized_expected_room_name and normalized_observed_room_name:
            room_mismatch = normalized_expected_room_name != normalized_observed_room_name
        else:
            room_mismatch = (
                expected_room_id is not None
                and observed_room_id is not None
                and expected_room_id != observed_room_id
            )

    if not room_mismatch:
        return ReconcileDecision(
            set_task_status_cleared_since_dispatch=set_task_status_cleared_since_dispatch,
            event_reasons=tuple(event_reasons),
        )

    if cleaning_progress is not None and cleaning_progress < active_room_mismatch_min_progress:
        event_reasons.append(
            (
                "active_room_mismatch_waiting_progress:"
                f"expected_{expected_room_id}:observed_{observed_room_id}:"
                f"progress_{cleaning_progress}:min_{active_room_mismatch_min_progress}"
            )
        )
        return ReconcileDecision(
            set_task_status_cleared_since_dispatch=set_task_status_cleared_since_dispatch,
            event_reasons=tuple(event_reasons),
        )

    if (
        cleaning_progress is not None
        and active_room_mismatch_max_progress is not None
        and cleaning_progress >= active_room_mismatch_max_progress
    ):
        event_reasons.append(
            (
                "active_room_mismatch_waiting_near_completion:"
                f"expected_{expected_room_id}:observed_{observed_room_id}:"
                f"progress_{cleaning_progress}:max_{active_room_mismatch_max_progress}"
            )
        )
        return ReconcileDecision(
            set_task_status_cleared_since_dispatch=set_task_status_cleared_since_dispatch,
            event_reasons=tuple(event_reasons),
        )

    next_mismatch_streak = int(active_room_mismatch_streak) + 1
    if next_mismatch_streak < int(active_room_mismatch_required_streak):
        event_reasons.append(
            (
                "active_room_mismatch_waiting_streak:"
                f"expected_{expected_room_id}:observed_{observed_room_id}:"
                f"streak_{next_mismatch_streak}"
            )
        )
        return ReconcileDecision(
            set_task_status_cleared_since_dispatch=set_task_status_cleared_since_dispatch,
            event_reasons=tuple(event_reasons),
        )

    if (
        seconds_since_last_command is not None
        and seconds_since_last_command >= dispatch_retry_interval_sec
    ):
        return ReconcileDecision(
            retry_current_room=True,
            set_task_status_cleared_since_dispatch=set_task_status_cleared_since_dispatch,
            event_reasons=tuple(
                event_reasons
                + [
                    (
                        f"active_room_mismatch_retry:{dispatch_retry_count + 1}:"
                        f"expected_{expected_room_id}:observed_{observed_room_id}"
                    )
                ]
            ),
        )

    event_reasons.append(
        (
            "active_room_mismatch_waiting_retry_interval:"
            f"expected_{expected_room_id}:observed_{observed_room_id}"
        )
    )
    return ReconcileDecision(
        set_task_status_cleared_since_dispatch=set_task_status_cleared_since_dispatch,
        event_reasons=tuple(event_reasons),
    )


def _finish_current_room(
    state: QueueState,
    *,
    next_status: str,
    result: str | None = None,
) -> QueueState:
    items, current_index, current_queue_item = _running_current_context(state)
    next_item_result = current_queue_item.result if result is None else result
    items[current_index] = replace(
        current_queue_item,
        status=next_status,
        result=next_item_result,
    )

    next_pending_index = _find_first_pending_index(items)
    if next_pending_index is None:
        return replace(
            state,
            run_state="completed",
            items=tuple(items),
            current_item_id=None,
        )

    next_item = items[next_pending_index]
    items[next_pending_index] = replace(next_item, status="running")
    return replace(state, items=tuple(items), current_item_id=next_item.item_id)


def _running_current_context(state: QueueState) -> tuple[list[QueueItem], int, QueueItem]:
    if state.run_state != "running":
        raise InvalidOperation("Queue is not running")
    if state.current_item_id is None:
        raise InvalidOperation("No current room is set")

    items = list(state.items)
    current_index = _find_index_by_id(items, state.current_item_id)
    current_queue_item = items[current_index]
    if current_queue_item.status != "running":
        raise InvalidOperation("Current room is not running")
    return items, current_index, current_queue_item


def _mark_non_terminal_items(items: tuple[QueueItem, ...], *, reason: str) -> tuple[QueueItem, ...]:
    updated: list[QueueItem] = []
    for item in items:
        if item.status in TERMINAL_ITEM_STATUSES:
            updated.append(item)
            continue
        updated.append(replace(item, status="canceled", result=reason))
    return tuple(updated)


def _find_index_by_id(items: list[QueueItem], item_id: str) -> int:
    for idx, item in enumerate(items):
        if item.item_id == item_id:
            return idx
    raise ItemNotFound(item_id)


def _find_running_index(items: list[QueueItem]) -> int | None:
    for idx, item in enumerate(items):
        if item.status == "running":
            return idx
    return None


def _find_first_pending_index(items: list[QueueItem]) -> int | None:
    for idx, item in enumerate(items):
        if item.status == "pending":
            return idx
    return None

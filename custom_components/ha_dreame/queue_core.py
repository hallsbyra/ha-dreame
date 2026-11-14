"""Pure queue core for HA Dreame orchestration."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime
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
class DispatchTracking:
    """Reconcile memory about the current room since its last robot command."""

    last_command_at: datetime
    dispatch_retry_count: int = 0
    active_room_confirmed_since_dispatch: bool = False
    task_status_cleared_since_dispatch: bool = False
    post_run_maintenance_seen: bool = False


@dataclass(frozen=True)
class QueueState:
    """Current queue state.

    `dispatch` belongs to the current room: transitions that change the current room
    clear it, and a room dispatch sets it.
    """

    run_state: str = "idle"
    run_id: str | None = None
    items: tuple[QueueItem, ...] = ()
    current_item_id: str | None = None
    dispatch: DispatchTracking | None = None


TERMINAL_ITEM_STATUSES = {"completed", "skipped", "needs_attention"}
FAILED_RUN_STATES = {"out_of_sync", "blocked"}
TERMINAL_RUN_STATES = {"completed", "canceled", *FAILED_RUN_STATES}


def new_state() -> QueueState:
    """Create an empty queue state."""
    return QueueState()


def add_room(
    state: QueueState,
    *,
    room_id: int,
    room_name: str,
    overrides: dict[str, Any] | None = None,
) -> QueueState:
    """Append one pending room, inheriting the previous item's overrides by default.

    Adding after a finished run starts a fresh queue. After a failed run it keeps the rooms that
    need review, since the robot may still be cleaning them and hiding them loses the only
    trace, and the remaining pending rooms, which can still run. The new room inherits from the
    last remaining room only.
    """
    if state.run_state in TERMINAL_RUN_STATES:
        kept = (
            tuple(item for item in state.items if item.status in {"needs_attention", "pending"})
            if state.run_state in FAILED_RUN_STATES
            else ()
        )
        state = QueueState(items=kept)
        if overrides is None:
            remaining = [item for item in kept if item.status == "pending"]
            overrides = remaining[-1].overrides if remaining else {}

    if overrides is None:
        overrides = state.items[-1].overrides if state.items else {}

    item = QueueItem(
        item_id=uuid4().hex,
        room_id=room_id,
        room_name=room_name,
        overrides=dict(overrides),
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
    if state.run_state == "waiting_for_tanks" and _find_first_pending_index(items) is None:
        return QueueState(items=tuple(items))
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
        dispatch=None,
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
        dispatch=None,
    )


def external_takeover(state: QueueState, *, reason: str, blocked: bool = False) -> QueueState:
    """Stop an uncertain run while preserving untouched queued rooms.

    The run ends `blocked` when the robot cannot reach the room, else `out_of_sync`.
    """
    items = list(state.items)
    if state.current_item_id is not None:
        try:
            current_index = _find_index_by_id(items, state.current_item_id)
        except ItemNotFound:
            pass
        else:
            current_queue_item = items[current_index]
            if current_queue_item.status not in TERMINAL_ITEM_STATUSES:
                items[current_index] = replace(
                    current_queue_item,
                    status="needs_attention",
                    result=reason,
                )
    return replace(
        state,
        run_state="blocked" if blocked else "out_of_sync",
        items=tuple(items),
        current_item_id=None,
        dispatch=None,
    )


def current_item(state: QueueState) -> QueueItem | None:
    """Return the current running queue item."""
    if state.current_item_id is None:
        return None
    for item in state.items:
        if item.item_id == state.current_item_id:
            return item
    return None


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
            dispatch=None,
        )

    next_item = items[next_pending_index]
    items[next_pending_index] = replace(next_item, status="running")
    return replace(state, items=tuple(items), current_item_id=next_item.item_id, dispatch=None)


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

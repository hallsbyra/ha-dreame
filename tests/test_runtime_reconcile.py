"""Tests for applying reconcile decisions to runtime state."""

import pytest

from custom_components.ha_dreame.queue_core import (
    InvalidOperation,
    QueueState,
    ReconcileDecision,
    add_room,
    start_run,
)
from custom_components.ha_dreame.runtime_reconcile import (
    COMMAND_INTENT_DISPATCH_CURRENT_ROOM,
    COMMAND_INTENT_RESUME_CURRENT_ROOM,
    apply_reconcile_decision,
)
from custom_components.ha_dreame.runtime_state import QueueRunTracking


def _seed_rooms(*rooms: tuple[int, str]) -> QueueState:
    state = QueueState()
    for room_id, room_name in rooms:
        state = add_room(state, room_id=room_id, room_name=room_name)
    return state


def _running_state() -> QueueState:
    return start_run(
        _seed_rooms(
            (1, "Kitchen"),
            (2, "Hall"),
        )
    )


def _tracking(state: QueueState, **overrides: object) -> QueueRunTracking:
    assert state.run_id is not None
    assert state.current_item_id is not None
    values = {
        "run_id": state.run_id,
        "current_item_id": state.current_item_id,
        "last_command_at": "2026-05-16T08:00:00+00:00",
    }
    values.update(overrides)
    return QueueRunTracking(**values)


def test_apply_reconcile_preserves_state_for_noop_decision() -> None:
    """Test no-op decisions leave queue and tracking untouched."""
    state = _running_state()
    tracking = _tracking(state)

    result = apply_reconcile_decision(
        state,
        tracking,
        ReconcileDecision(event_reasons=("vacuum_paused_waiting",)),
    )

    assert result.queue_state == state
    assert result.run_tracking == tracking
    assert result.command_intent is None
    assert result.command_item_id is None
    assert result.event_reasons == ("vacuum_paused_waiting",)


def test_apply_reconcile_updates_tracking_flags() -> None:
    """Test tracking-only decisions update runtime tracking."""
    state = _running_state()
    tracking = _tracking(
        state,
        dispatch_retry_count=2,
        task_status_cleared_since_dispatch=False,
    )

    result = apply_reconcile_decision(
        state,
        tracking,
        ReconcileDecision(
            set_task_status_cleared_since_dispatch=True,
            reset_dispatch_retry_count=True,
            event_reasons=("task_status_cleared_after_dispatch",),
        ),
    )

    assert result.queue_state == state
    assert result.run_tracking is not None
    assert result.run_tracking.dispatch_retry_count == 0
    assert result.run_tracking.task_status_cleared_since_dispatch is True
    assert result.command_intent is None
    assert result.event_reasons == ("task_status_cleared_after_dispatch",)


def test_apply_reconcile_retry_returns_dispatch_intent_and_increments_retry() -> None:
    """Test retry decisions ask the caller to dispatch the current room later."""
    state = _running_state()
    tracking = _tracking(state, dispatch_retry_count=1)

    result = apply_reconcile_decision(
        state,
        tracking,
        ReconcileDecision(
            retry_current_room=True,
            event_reasons=("retry_dispatch_requested:2",),
        ),
    )

    assert result.queue_state == state
    assert result.run_tracking is not None
    assert result.run_tracking.dispatch_retry_count == 2
    assert result.run_tracking.last_command_at == tracking.last_command_at
    assert result.command_intent == COMMAND_INTENT_DISPATCH_CURRENT_ROOM
    assert result.command_item_id == state.current_item_id
    assert result.event_reasons == ("retry_dispatch_requested:2",)


def test_apply_reconcile_resume_returns_resume_intent() -> None:
    """Test resume decisions ask the caller to resume without dispatching a room plan."""
    state = _running_state()
    tracking = _tracking(state)

    result = apply_reconcile_decision(
        state,
        tracking,
        ReconcileDecision(
            resume_current_room=True,
            event_reasons=("dock_prep_paused_resume_requested",),
        ),
    )

    assert result.queue_state == state
    assert result.run_tracking == tracking
    assert result.command_intent == COMMAND_INTENT_RESUME_CURRENT_ROOM
    assert result.command_item_id == state.current_item_id


def test_apply_reconcile_completion_advances_and_requests_next_dispatch() -> None:
    """Test completing a room clears old tracking and exposes the next dispatch need."""
    state = _running_state()
    tracking = _tracking(state)

    result = apply_reconcile_decision(
        state,
        tracking,
        ReconcileDecision(
            complete_current_room=True,
            event_reasons=("task_status_completed",),
        ),
    )

    assert result.queue_state.run_state == "running"
    assert [item.status for item in result.queue_state.items] == [
        "completed",
        "running",
    ]
    assert result.queue_state.current_item_id == result.queue_state.items[1].item_id
    assert result.run_tracking is None
    assert result.command_intent == COMMAND_INTENT_DISPATCH_CURRENT_ROOM
    assert result.command_item_id == result.queue_state.items[1].item_id
    assert result.event_reasons == ("task_status_completed",)


def test_apply_reconcile_completion_finishes_last_room_without_dispatch() -> None:
    """Test completing the final room clears tracking without a dispatch intent."""
    state = start_run(_seed_rooms((1, "Kitchen")))
    tracking = _tracking(state)

    result = apply_reconcile_decision(
        state,
        tracking,
        ReconcileDecision(complete_current_room=True),
    )

    assert result.queue_state.run_state == "completed"
    assert result.queue_state.current_item_id is None
    assert result.run_tracking is None
    assert result.command_intent is None
    assert result.command_item_id is None


def test_apply_reconcile_out_of_sync_clears_tracking() -> None:
    """Test out-of-sync decisions terminally mark the queue and clear tracking."""
    state = _running_state()
    tracking = _tracking(state)

    result = apply_reconcile_decision(
        state,
        tracking,
        ReconcileDecision(
            mark_out_of_sync_reason="dispatch_retry_exhausted:expected_1:observed_7",
            event_reasons=("dispatch_retry_exhausted",),
        ),
    )

    assert result.queue_state.run_state == "out_of_sync"
    assert result.queue_state.current_item_id is None
    assert [item.status for item in result.queue_state.items] == [
        "canceled",
        "canceled",
    ]
    assert result.run_tracking is None
    assert result.command_intent is None
    assert result.event_reasons == ("dispatch_retry_exhausted",)


def test_apply_reconcile_route_error_marks_queue_blocked() -> None:
    """Test route errors use the existing blocked terminal queue state."""
    state = _running_state()
    tracking = _tracking(state)

    result = apply_reconcile_decision(
        state,
        tracking,
        ReconcileDecision(
            mark_out_of_sync_reason="vacuum_route_error:expected_1:observed_7",
        ),
    )

    assert result.queue_state.run_state == "blocked"
    assert result.run_tracking is None


def test_apply_reconcile_rejects_effectful_decision_without_tracking() -> None:
    """Test effectful decisions require runtime tracking."""
    state = _running_state()

    with pytest.raises(InvalidOperation, match="requires run tracking"):
        apply_reconcile_decision(
            state,
            None,
            ReconcileDecision(retry_current_room=True),
        )


def test_apply_reconcile_rejects_stale_tracking() -> None:
    """Test decisions cannot mutate a queue with tracking from another run or item."""
    state = _running_state()
    stale_tracking = QueueRunTracking(
        run_id="old-run",
        current_item_id=state.current_item_id or "missing",
        last_command_at="2026-05-16T08:00:00+00:00",
    )

    with pytest.raises(InvalidOperation, match="does not match current queue run"):
        apply_reconcile_decision(
            state,
            stale_tracking,
            ReconcileDecision(retry_current_room=True),
        )

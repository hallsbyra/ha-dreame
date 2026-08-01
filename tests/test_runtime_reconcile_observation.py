"""Tests for runtime reconcile observation evaluation."""

from datetime import datetime, timedelta, timezone

from custom_components.ha_dreame.queue_core import (
    QueueState,
    ReconcileDecision,
    add_room,
    start_run,
)
from custom_components.ha_dreame.runtime_reconcile_observation import (
    RuntimeReconcileObservation,
    RuntimeReconcileSettings,
    evaluate_runtime_reconcile_observation,
)
from custom_components.ha_dreame.runtime_state import QueueRunTracking


NOW = datetime(2026, 5, 17, 8, 0, tzinfo=timezone.utc)


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
        "last_command_at": (NOW - timedelta(seconds=10)).isoformat(),
        "task_status_cleared_since_dispatch": True,
    }
    values.update(overrides)
    return QueueRunTracking(**values)


def test_evaluate_observation_noops_when_queue_is_not_running() -> None:
    """Test observation evaluation waits for an active tracked queue run."""
    evaluation = evaluate_runtime_reconcile_observation(
        _seed_rooms((1, "Kitchen")),
        None,
        RuntimeReconcileObservation(
            vacuum_state="cleaning",
            task_status="room_cleaning",
            observed_room_id=1,
        ),
        now=NOW,
    )

    assert evaluation.awaiting_completion_event is False
    assert evaluation.decision == ReconcileDecision()


def test_evaluate_observation_completed_requires_cleared_task_status() -> None:
    """Test stale completed status immediately after dispatch is ignored."""
    state = _running_state()

    evaluation = evaluate_runtime_reconcile_observation(
        state,
        _tracking(state, task_status_cleared_since_dispatch=False),
        RuntimeReconcileObservation(
            vacuum_state="idle",
            task_status="completed",
            observed_room_id=1,
        ),
        now=NOW,
    )

    assert evaluation.decision.complete_current_room is False
    assert evaluation.decision.retry_current_room is False
    assert evaluation.decision.event_reasons == (
        "task_status_completed_ignored_not_cleared_after_dispatch",
    )


def test_evaluate_observation_completed_after_cleared_status_completes_room() -> None:
    """Test completed status can complete the tracked current room."""
    state = _running_state()

    evaluation = evaluate_runtime_reconcile_observation(
        state,
        _tracking(state, task_status_cleared_since_dispatch=True),
        RuntimeReconcileObservation(
            vacuum_state="idle",
            task_status="completed",
            observed_room_id=1,
        ),
        now=NOW,
    )

    assert evaluation.expected_room_id == 1
    assert evaluation.expected_room_name == "Kitchen"
    assert evaluation.decision.complete_current_room is True
    assert evaluation.decision.event_reasons == ("task_status_completed",)


def test_evaluate_observation_active_match_sets_cleared_flag() -> None:
    """Test active matching status clears stale dispatch task status."""
    state = _running_state()

    evaluation = evaluate_runtime_reconcile_observation(
        state,
        _tracking(state, task_status_cleared_since_dispatch=False),
        RuntimeReconcileObservation(
            vacuum_state="cleaning",
            task_status="room_cleaning",
            observed_room_id=1,
        ),
        now=NOW,
    )

    assert evaluation.seconds_since_last_command == 10
    assert evaluation.decision.set_task_status_cleared_since_dispatch is True
    assert evaluation.decision.retry_current_room is False
    assert evaluation.decision.event_reasons == ("task_status_cleared_after_dispatch",)


def test_evaluate_observation_delayed_non_active_state_retries() -> None:
    """Test inactive robot observations can request redispatch after the interval."""
    state = _running_state()

    evaluation = evaluate_runtime_reconcile_observation(
        state,
        _tracking(state, last_command_at=(NOW - timedelta(seconds=30)).isoformat()),
        RuntimeReconcileObservation(
            vacuum_state="idle",
            task_status="room_cleaning",
            observed_room_id=1,
        ),
        now=NOW,
        settings=RuntimeReconcileSettings(dispatch_retry_interval_sec=20),
    )

    assert evaluation.decision.retry_current_room is True
    assert evaluation.decision.mark_out_of_sync_reason is None
    assert evaluation.decision.event_reasons == ("retry_dispatch_requested:1",)


def test_evaluate_observation_active_room_mismatch_can_retry() -> None:
    """Test observed wrong-room cleaning delegates to mismatch retry logic."""
    state = _running_state()

    evaluation = evaluate_runtime_reconcile_observation(
        state,
        _tracking(
            state,
            active_room_mismatch_streak=1,
            dispatch_retry_count=1,
            last_command_at=(NOW - timedelta(seconds=30)).isoformat(),
        ),
        RuntimeReconcileObservation(
            vacuum_state="cleaning",
            task_status="room_cleaning",
            observed_room_id=7,
            cleaning_progress=20,
        ),
        now=NOW,
        settings=RuntimeReconcileSettings(
            active_room_mismatch_required_streak=2,
            dispatch_retry_interval_sec=20,
        ),
    )

    assert evaluation.observed_room_id == 7
    assert evaluation.decision.retry_current_room is True
    assert evaluation.decision.event_reasons == (
        "active_room_mismatch_retry:2:expected_1:observed_7",
    )


def test_evaluate_observation_late_room_mismatch_uses_default_completion_guard() -> None:
    """Test default runtime settings suppress redispatch near completion."""
    state = _running_state()

    evaluation = evaluate_runtime_reconcile_observation(
        state,
        _tracking(
            state,
            active_room_confirmed_since_dispatch=True,
            active_room_mismatch_streak=1,
            last_command_at=(NOW - timedelta(seconds=30)).isoformat(),
        ),
        RuntimeReconcileObservation(
            vacuum_state="cleaning",
            task_status="room_cleaning",
            observed_room_id=7,
            cleaning_progress=95,
        ),
        now=NOW,
    )

    assert evaluation.decision.retry_current_room is False
    assert evaluation.decision.event_reasons == (
        "active_room_mismatch_waiting_near_completion:expected_1:observed_7:progress_95:max_90",
    )


def test_evaluate_observation_mop_maintenance_waits_without_retry() -> None:
    """Test explicit mop-maintenance observations do not consume retry budget."""
    state = _running_state()

    evaluation = evaluate_runtime_reconcile_observation(
        state,
        _tracking(
            state,
            dispatch_retry_count=2,
            last_command_at=(NOW - timedelta(seconds=120)).isoformat(),
        ),
        RuntimeReconcileObservation(
            vacuum_state="docked",
            task_status="room_cleaning",
            observed_room_id=7,
            is_mop_maintenance_state=True,
        ),
        now=NOW,
        settings=RuntimeReconcileSettings(dispatch_retry_max=2),
    )

    assert evaluation.decision.retry_current_room is False
    assert evaluation.decision.mark_out_of_sync_reason is None
    assert evaluation.decision.event_reasons == ("mop_maintenance_waiting",)


def test_evaluate_observation_bad_command_timestamp_does_not_retry() -> None:
    """Test invalid command timestamps do not fabricate elapsed retry time."""
    state = _running_state()

    evaluation = evaluate_runtime_reconcile_observation(
        state,
        _tracking(state, last_command_at="not-a-timestamp"),
        RuntimeReconcileObservation(
            vacuum_state="idle",
            task_status="room_cleaning",
            observed_room_id=1,
        ),
        now=NOW,
        settings=RuntimeReconcileSettings(dispatch_retry_interval_sec=20),
    )

    assert evaluation.seconds_since_last_command is None
    assert evaluation.decision.retry_current_room is False
    assert evaluation.decision.mark_out_of_sync_reason is None


def test_evaluate_observation_naive_command_timestamp_does_not_retry() -> None:
    """Test timezone-naive command timestamps are treated as elapsed-time unknown."""
    state = _running_state()

    evaluation = evaluate_runtime_reconcile_observation(
        state,
        _tracking(state, last_command_at="2026-05-17T07:00:00"),
        RuntimeReconcileObservation(
            vacuum_state="idle",
            task_status="room_cleaning",
            observed_room_id=1,
        ),
        now=NOW,
        settings=RuntimeReconcileSettings(dispatch_retry_interval_sec=20),
    )

    assert evaluation.seconds_since_last_command is None
    assert evaluation.decision.retry_current_room is False
    assert evaluation.decision.mark_out_of_sync_reason is None

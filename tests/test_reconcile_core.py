"""Tests for pure reconciliation decisions."""

from custom_components.ha_dreame.queue_core import (
    ReconcileDecision,
    evaluate_reconcile_tick,
)


ACTIVE_STATES = {"cleaning", "returning"}


def _decision(**overrides: object) -> ReconcileDecision:
    kwargs = {
        "vacuum_state": "cleaning",
        "task_status": "room_cleaning",
        "awaiting_completion_event": True,
        "seconds_since_last_command": 5,
        "task_status_cleared_since_dispatch": True,
        "dispatch_retry_count": 0,
        "expected_room_id": 1,
        "observed_room_id": 1,
        "is_dock_prep_state": False,
        "active_states": ACTIVE_STATES,
        "dispatch_retry_interval_sec": 20,
        "dispatch_retry_max": 2,
    }
    kwargs.update(overrides)
    return evaluate_reconcile_tick(**kwargs)


def test_reconcile_noop_when_not_awaiting_completion() -> None:
    """Test reconciliation does nothing when no room is awaiting completion."""
    decision = _decision(awaiting_completion_event=False)

    assert decision == ReconcileDecision()


def test_reconcile_sets_task_status_cleared_after_dispatch() -> None:
    """Test non-completed task status enables later completion."""
    decision = _decision(task_status_cleared_since_dispatch=False)

    assert decision.set_task_status_cleared_since_dispatch is True
    assert decision.complete_current_room is False
    assert decision.retry_current_room is False
    assert decision.event_reasons == ("task_status_cleared_after_dispatch",)


def test_reconcile_stale_completed_status_does_not_complete_room() -> None:
    """Test stale completed task status after dispatch is ignored."""
    decision = _decision(
        vacuum_state="idle",
        task_status="completed",
        task_status_cleared_since_dispatch=False,
        seconds_since_last_command=10,
    )

    assert decision.complete_current_room is False
    assert decision.retry_current_room is False
    assert decision.mark_out_of_sync_reason is None
    assert decision.event_reasons == ("task_status_completed_ignored_not_cleared_after_dispatch",)


def test_reconcile_completed_after_status_cleared_completes_room() -> None:
    """Test completed status can complete only after task status was cleared."""
    decision = _decision(
        vacuum_state="idle",
        task_status="completed",
        task_status_cleared_since_dispatch=True,
        seconds_since_last_command=30,
    )

    assert decision.complete_current_room is True
    assert decision.retry_current_room is False
    assert decision.mark_out_of_sync_reason is None
    assert decision.event_reasons == ("task_status_completed",)


def test_reconcile_route_error_marks_blocked() -> None:
    """Test route errors become terminal blocked decisions."""
    decision = _decision(
        vacuum_state="error",
        task_status="completed",
        vacuum_error_code="route",
        expected_room_id=1,
        observed_room_id=7,
    )

    assert decision.complete_current_room is False
    assert decision.retry_current_room is False
    assert decision.mark_out_of_sync_reason == "vacuum_route_error:expected_1:observed_7"
    assert decision.event_reasons == ("vacuum_error_route_blocked",)


def test_reconcile_recoverable_error_waits_and_resets_retry_count() -> None:
    """Test robot error states hold orchestration for user/recovery action."""
    decision = _decision(
        vacuum_state="error",
        task_status="room_cleaning",
        vacuum_error_code="water_tank_dry",
        dispatch_retry_count=2,
        seconds_since_last_command=120,
    )

    assert decision.complete_current_room is False
    assert decision.retry_current_room is False
    assert decision.mark_out_of_sync_reason is None
    assert decision.reset_dispatch_retry_count is True
    assert decision.event_reasons == ("vacuum_error_waiting_user_action",)


def test_reconcile_non_fatal_error_reports_non_fatal_reason() -> None:
    """Test configured non-fatal errors are surfaced without failing the run."""
    decision = _decision(
        vacuum_state="error",
        task_status="room_cleaning",
        vacuum_error_code="remove_mop",
        non_fatal_error_codes={"remove_mop"},
        seconds_since_last_command=120,
    )

    assert decision.complete_current_room is False
    assert decision.retry_current_room is False
    assert decision.mark_out_of_sync_reason is None
    assert decision.reset_dispatch_retry_count is True
    assert decision.event_reasons == ("vacuum_error_non_fatal:remove_mop",)


def test_reconcile_dock_prep_pause_waits_for_resume_ready() -> None:
    """Test dock-prep pause does not retry while resume prerequisites are missing."""
    decision = _decision(
        vacuum_state="cleaning",
        task_status="room_cleaning",
        is_dock_prep_state=True,
        is_dock_prep_paused=True,
        dock_prep_resume_ready=False,
        seconds_since_last_command=120,
    )

    assert decision.retry_current_room is False
    assert decision.resume_current_room is False
    assert decision.mark_out_of_sync_reason is None
    assert decision.event_reasons == ("dock_prep_paused_waiting_resume_ready",)


def test_reconcile_dock_prep_pause_with_blocking_error_waits_for_user_action() -> None:
    """Test dock-prep pause with an error waits instead of resuming."""
    decision = _decision(
        vacuum_state="cleaning",
        task_status="room_cleaning",
        vacuum_error_code="water_tank_dry",
        is_dock_prep_state=True,
        is_dock_prep_paused=True,
        dock_prep_resume_ready=True,
        seconds_since_last_command=120,
    )

    assert decision.retry_current_room is False
    assert decision.resume_current_room is False
    assert decision.reset_dispatch_retry_count is True
    assert decision.event_reasons == ("vacuum_error_waiting_user_action",)


def test_reconcile_dock_prep_pause_waits_for_retry_interval() -> None:
    """Test dock-prep resume waits for the retry interval."""
    decision = _decision(
        vacuum_state="cleaning",
        task_status="room_cleaning",
        is_dock_prep_state=True,
        is_dock_prep_paused=True,
        dock_prep_resume_ready=True,
        seconds_since_last_command=10,
        dispatch_retry_interval_sec=20,
    )

    assert decision.retry_current_room is False
    assert decision.resume_current_room is False
    assert decision.event_reasons == ("dock_prep_paused_waiting_retry_interval",)


def test_reconcile_dock_prep_pause_requests_resume_when_ready() -> None:
    """Test dock-prep pause asks runtime layer to resume once safe."""
    decision = _decision(
        vacuum_state="cleaning",
        task_status="room_cleaning",
        is_dock_prep_state=True,
        is_dock_prep_paused=True,
        dock_prep_resume_ready=True,
        seconds_since_last_command=120,
        dispatch_retry_interval_sec=20,
    )

    assert decision.retry_current_room is False
    assert decision.resume_current_room is True
    assert decision.event_reasons == ("dock_prep_paused_resume_requested",)


def test_reconcile_paused_robot_waits_without_retry() -> None:
    """Test paused robot/task states are treated as hold states."""
    decision = _decision(
        vacuum_state="paused",
        task_status="room_cleaning_paused",
        seconds_since_last_command=120,
    )

    assert decision.retry_current_room is False
    assert decision.mark_out_of_sync_reason is None
    assert decision.event_reasons == ("vacuum_paused_waiting",)


def test_reconcile_paused_robot_with_blocking_error_waits_for_user_action() -> None:
    """Test paused robot with an error stays in recoverable hold."""
    decision = _decision(
        vacuum_state="paused",
        task_status="room_cleaning_paused",
        vacuum_error_code="water_tank_dry",
        seconds_since_last_command=120,
    )

    assert decision.retry_current_room is False
    assert decision.mark_out_of_sync_reason is None
    assert decision.reset_dispatch_retry_count is True
    assert decision.event_reasons == ("vacuum_error_waiting_user_action",)


def test_reconcile_matching_room_names_suppress_room_id_mismatch() -> None:
    """Test room names are preferred over unstable room ids when available."""
    decision = _decision(
        vacuum_state="cleaning",
        expected_room_id=1,
        observed_room_id=7,
        expected_room_name="Hall",
        observed_room_name="Hall",
        seconds_since_last_command=120,
    )

    assert decision.retry_current_room is False
    assert decision.mark_out_of_sync_reason is None
    assert not any(reason.startswith("active_room_mismatch") for reason in decision.event_reasons)


def test_reconcile_room_id_mismatch_retries_when_names_are_missing() -> None:
    """Test room ids are used when names are unavailable."""
    decision = _decision(
        vacuum_state="cleaning",
        expected_room_id=1,
        observed_room_id=7,
        expected_room_name=None,
        observed_room_name=None,
        seconds_since_last_command=120,
    )

    assert decision.retry_current_room is True
    assert any(
        reason.startswith("active_room_mismatch_retry:") for reason in decision.event_reasons
    )


def test_reconcile_early_room_mismatch_waits_for_min_progress() -> None:
    """Test early room mismatch is treated as transition noise."""
    decision = _decision(
        vacuum_state="cleaning",
        expected_room_name="Kitchen",
        observed_room_name="Hall",
        cleaning_progress=0,
        active_room_mismatch_min_progress=5,
        seconds_since_last_command=120,
    )

    assert decision.retry_current_room is False
    assert any(
        reason.startswith("active_room_mismatch_waiting_progress:")
        for reason in decision.event_reasons
    )


def test_reconcile_late_room_mismatch_waits_near_completion() -> None:
    """Test near-completion room mismatch does not restart an almost-finished room."""
    decision = _decision(
        vacuum_state="cleaning",
        expected_room_name="Kitchen",
        observed_room_name="Hall",
        cleaning_progress=95,
        active_room_mismatch_min_progress=5,
        active_room_mismatch_max_progress=90,
        active_room_mismatch_streak=3,
        active_room_mismatch_required_streak=2,
        seconds_since_last_command=120,
    )

    assert decision.retry_current_room is False
    assert any(
        reason.startswith("active_room_mismatch_waiting_near_completion:")
        for reason in decision.event_reasons
    )


def test_reconcile_room_mismatch_waits_for_required_streak() -> None:
    """Test room mismatch must persist long enough before retry."""
    decision = _decision(
        vacuum_state="cleaning",
        expected_room_name="Kitchen",
        observed_room_name="Hall",
        cleaning_progress=20,
        active_room_mismatch_streak=0,
        active_room_mismatch_required_streak=2,
        seconds_since_last_command=120,
    )

    assert decision.retry_current_room is False
    assert any(
        reason.startswith("active_room_mismatch_waiting_streak:")
        for reason in decision.event_reasons
    )


def test_reconcile_room_mismatch_waits_for_retry_interval() -> None:
    """Test room mismatch retry waits for command retry interval."""
    decision = _decision(
        vacuum_state="cleaning",
        expected_room_name="Kitchen",
        observed_room_name="Hall",
        cleaning_progress=20,
        active_room_mismatch_streak=2,
        active_room_mismatch_required_streak=2,
        seconds_since_last_command=5,
        dispatch_retry_interval_sec=20,
    )

    assert decision.retry_current_room is False
    assert any(
        reason.startswith("active_room_mismatch_waiting_retry_interval:")
        for reason in decision.event_reasons
    )


def test_reconcile_room_mismatch_retries_after_streak_and_interval() -> None:
    """Test sustained room mismatch requests a retry."""
    decision = _decision(
        vacuum_state="cleaning",
        expected_room_name="Kitchen",
        observed_room_name="Hall",
        cleaning_progress=20,
        active_room_mismatch_streak=2,
        active_room_mismatch_required_streak=2,
        dispatch_retry_count=1,
        seconds_since_last_command=120,
        dispatch_retry_interval_sec=20,
    )

    assert decision.retry_current_room is True
    assert decision.mark_out_of_sync_reason is None
    assert any(
        reason.startswith("active_room_mismatch_retry:2:") for reason in decision.event_reasons
    )


def test_reconcile_non_active_state_retries_after_interval() -> None:
    """Test non-active robot state triggers redispatch after the retry interval."""
    decision = _decision(
        vacuum_state="idle",
        task_status="room_cleaning",
        seconds_since_last_command=30,
        dispatch_retry_interval_sec=20,
        dispatch_retry_count=0,
    )

    assert decision.retry_current_room is True
    assert decision.mark_out_of_sync_reason is None
    assert decision.event_reasons == ("retry_dispatch_requested:1",)


def test_reconcile_non_active_state_escalates_after_retry_budget() -> None:
    """Test retry budget exhaustion escalates to out_of_sync."""
    decision = _decision(
        vacuum_state="idle",
        task_status="room_cleaning",
        seconds_since_last_command=30,
        dispatch_retry_interval_sec=20,
        dispatch_retry_count=2,
        dispatch_retry_max=2,
        expected_room_id=1,
        observed_room_id=7,
    )

    assert decision.retry_current_room is False
    assert decision.mark_out_of_sync_reason == (
        "dispatch_retry_exhausted:expected_1:observed_7:vacuum_idle"
    )
    assert decision.event_reasons == ("dispatch_retry_exhausted",)

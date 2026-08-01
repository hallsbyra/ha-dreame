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


def test_reconcile_completed_unconfirmed_wrong_room_marks_out_of_sync() -> None:
    """Test a completed foreign task cannot complete the queued room."""
    decision = _decision(
        vacuum_state="idle",
        task_status="completed",
        task_status_cleared_since_dispatch=True,
        expected_room_id=3,
        observed_room_id=1,
        expected_room_name="Dining Room",
        observed_room_name="Porch",
        active_room_confirmed_since_dispatch=False,
    )

    assert decision.complete_current_room is False
    assert decision.retry_current_room is False
    assert decision.mark_out_of_sync_reason == (
        "task_completed_unconfirmed_room:expected_3:observed_1"
    )
    assert decision.event_reasons == ("task_status_completed_unconfirmed_room",)


def test_reconcile_completed_after_manual_pause_return_marks_out_of_sync() -> None:
    """Test manual pause followed by return does not complete the room."""
    decision = _decision(
        vacuum_state="returning",
        task_status="completed",
        pause_waiting_seen=True,
        is_returning_state=True,
        seconds_since_last_command=30,
    )

    assert decision.complete_current_room is False
    assert decision.retry_current_room is False
    assert decision.mark_out_of_sync_reason == "manual_return_to_dock_after_pause"
    assert decision.event_reasons == ("task_status_completed_after_manual_pause_returning",)


def test_reconcile_stale_completed_status_retries_after_interval() -> None:
    """Test stale completed status falls through to retry recovery."""
    decision = _decision(
        vacuum_state="idle",
        task_status="completed",
        task_status_cleared_since_dispatch=False,
        seconds_since_last_command=30,
        dispatch_retry_interval_sec=20,
    )

    assert decision.complete_current_room is False
    assert decision.retry_current_room is True
    assert decision.mark_out_of_sync_reason is None
    assert decision.event_reasons == (
        "task_status_completed_ignored_not_cleared_after_dispatch",
        "retry_dispatch_requested:1",
    )


def test_reconcile_stale_completed_status_escalates_after_retry_budget() -> None:
    """Test stale completed status can still exhaust retry budget."""
    decision = _decision(
        vacuum_state="idle",
        task_status="completed",
        task_status_cleared_since_dispatch=False,
        seconds_since_last_command=30,
        dispatch_retry_count=2,
        dispatch_retry_max=2,
        expected_room_id=1,
        observed_room_id=7,
    )

    assert decision.complete_current_room is False
    assert decision.retry_current_room is False
    assert decision.mark_out_of_sync_reason == (
        "dispatch_retry_exhausted:expected_1:observed_7:vacuum_idle"
    )
    assert decision.event_reasons == (
        "task_status_completed_ignored_not_cleared_after_dispatch",
        "dispatch_retry_exhausted",
    )


def test_reconcile_stale_completed_status_waits_during_dock_prep() -> None:
    """Test stale completed status does not retry while dock prep is active."""
    decision = _decision(
        vacuum_state="docked",
        task_status="completed",
        task_status_cleared_since_dispatch=False,
        is_dock_prep_state=True,
        seconds_since_last_command=120,
    )

    assert decision.complete_current_room is False
    assert decision.retry_current_room is False
    assert decision.mark_out_of_sync_reason is None
    assert decision.event_reasons == ("task_status_completed_ignored_not_cleared_after_dispatch",)


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


def test_reconcile_error_state_ignores_completed_status() -> None:
    """Test completed status does not complete while vacuum is in error."""
    decision = _decision(
        vacuum_state="error",
        task_status="completed",
        vacuum_error_code="water_tank_dry",
        task_status_cleared_since_dispatch=True,
        seconds_since_last_command=120,
    )

    assert decision.complete_current_room is False
    assert decision.retry_current_room is False
    assert decision.mark_out_of_sync_reason is None
    assert decision.reset_dispatch_retry_count is True
    assert decision.event_reasons == (
        "task_status_completed_ignored_due_vacuum_error:water_tank_dry",
        "vacuum_error_waiting_user_action",
    )


def test_reconcile_error_state_with_stale_completed_waits_for_recovery() -> None:
    """Test stale completed status in error state waits for recovery."""
    decision = _decision(
        vacuum_state="error",
        task_status="completed",
        task_status_cleared_since_dispatch=False,
        seconds_since_last_command=120,
        dispatch_retry_count=2,
    )

    assert decision.complete_current_room is False
    assert decision.retry_current_room is False
    assert decision.mark_out_of_sync_reason is None
    assert decision.reset_dispatch_retry_count is True
    assert decision.event_reasons == (
        "task_status_completed_ignored_not_cleared_after_dispatch",
        "vacuum_error_waiting_user_action",
    )


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


def test_reconcile_force_retry_after_error_recovery_ignores_interval_and_budget() -> None:
    """Test recovery retry bypasses normal interval and exhausted retry budget."""
    decision = _decision(
        vacuum_state="docked",
        task_status="room_cleaning",
        seconds_since_last_command=1,
        dispatch_retry_count=2,
        dispatch_retry_max=2,
        force_retry_after_recovery=True,
    )

    assert decision.complete_current_room is False
    assert decision.retry_current_room is True
    assert decision.mark_out_of_sync_reason is None
    assert decision.event_reasons == ("retry_dispatch_after_error_recovery",)


def test_reconcile_force_retry_after_error_recovery_noops_when_active() -> None:
    """Test recovery retry does nothing once robot is already active."""
    decision = _decision(
        vacuum_state="cleaning",
        task_status="room_cleaning",
        force_retry_after_recovery=True,
    )

    assert decision.complete_current_room is False
    assert decision.retry_current_room is False
    assert decision.mark_out_of_sync_reason is None
    assert decision.event_reasons == ()


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


def test_reconcile_dock_prep_pause_reports_non_fatal_error() -> None:
    """Test non-fatal error names are preserved during dock-prep pause."""
    decision = _decision(
        vacuum_state="cleaning",
        task_status="room_cleaning",
        vacuum_error_code="remove_mop",
        non_fatal_error_codes={"remove_mop"},
        is_dock_prep_state=True,
        is_dock_prep_paused=True,
        dock_prep_resume_ready=True,
        seconds_since_last_command=120,
    )

    assert decision.retry_current_room is False
    assert decision.resume_current_room is False
    assert decision.reset_dispatch_retry_count is True
    assert decision.event_reasons == ("vacuum_error_non_fatal:remove_mop",)


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


def test_reconcile_mop_remove_transition_waits_without_retry_or_out_of_sync() -> None:
    """Test mop removal maintenance does not consume dispatch retry budget."""
    decision = _decision(
        vacuum_state="docked",
        task_status="returning_to_remove_mop",
        vacuum_error_code="no_error",
        seconds_since_last_command=300,
        task_status_cleared_since_dispatch=True,
        dispatch_retry_count=2,
        expected_room_id=3,
        observed_room_id=7,
        expected_room_name="Dining room",
        observed_room_name="Hall",
        cleaning_progress=68,
        is_dock_prep_state=False,
        dispatch_retry_interval_sec=20,
        dispatch_retry_max=2,
    )

    assert decision.complete_current_room is False
    assert decision.retry_current_room is False
    assert decision.mark_out_of_sync_reason is None
    assert decision.reset_dispatch_retry_count is False
    assert decision.event_reasons == ("mop_maintenance_waiting",)


def test_reconcile_mop_install_robot_state_suppresses_active_room_mismatch_retry() -> None:
    """Test mop install maintenance suppresses active-room mismatch retries."""
    decision = _decision(
        vacuum_state="cleaning",
        task_status="room_cleaning",
        vacuum_error_code="no_error",
        seconds_since_last_command=300,
        task_status_cleared_since_dispatch=True,
        dispatch_retry_count=1,
        expected_room_id=3,
        observed_room_id=7,
        expected_room_name="Dining room",
        observed_room_name="Hall",
        cleaning_progress=69,
        active_room_mismatch_streak=1,
        active_room_mismatch_required_streak=2,
        is_dock_prep_state=False,
        dispatch_retry_interval_sec=20,
        dispatch_retry_max=2,
        is_mop_maintenance_state=True,
    )

    assert decision.complete_current_room is False
    assert decision.retry_current_room is False
    assert decision.mark_out_of_sync_reason is None
    assert decision.event_reasons == ("mop_maintenance_waiting",)


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


def test_reconcile_paused_robot_reports_non_fatal_error() -> None:
    """Test non-fatal error names are preserved while paused."""
    decision = _decision(
        vacuum_state="paused",
        task_status="room_cleaning_paused",
        vacuum_error_code="remove_mop",
        non_fatal_error_codes={"remove_mop"},
        seconds_since_last_command=120,
    )

    assert decision.retry_current_room is False
    assert decision.mark_out_of_sync_reason is None
    assert decision.reset_dispatch_retry_count is True
    assert decision.event_reasons == ("vacuum_error_non_fatal:remove_mop",)


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
        observed_room_id=7,
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


def test_reconcile_unconfirmed_late_room_mismatch_marks_out_of_sync() -> None:
    """Test an unconfirmed wrong-room run cannot hide behind high progress."""
    decision = _decision(
        vacuum_state="cleaning",
        observed_room_id=7,
        expected_room_name="Kitchen",
        observed_room_name="Hall",
        cleaning_progress=95,
        active_room_mismatch_min_progress=5,
        active_room_mismatch_max_progress=90,
        active_room_mismatch_streak=3,
        active_room_mismatch_required_streak=2,
        active_room_confirmed_since_dispatch=False,
        seconds_since_last_command=120,
    )

    assert decision.retry_current_room is False
    assert decision.mark_out_of_sync_reason == (
        "active_room_mismatch_unconfirmed_near_completion:expected_1:observed_7"
    )
    assert decision.event_reasons == (
        "active_room_mismatch_unconfirmed_near_completion:expected_1:observed_7:progress_95:max_90",
    )


def test_reconcile_confirmed_late_room_mismatch_waits_near_completion() -> None:
    """Test a late room flip is tolerated after the target room was confirmed."""
    decision = _decision(
        vacuum_state="cleaning",
        expected_room_name="Kitchen",
        observed_room_name="Hall",
        cleaning_progress=95,
        active_room_mismatch_min_progress=5,
        active_room_mismatch_max_progress=90,
        active_room_mismatch_streak=3,
        active_room_mismatch_required_streak=2,
        active_room_confirmed_since_dispatch=True,
        seconds_since_last_command=120,
    )

    assert decision.retry_current_room is False
    assert decision.mark_out_of_sync_reason is None
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


def test_reconcile_room_mismatch_exhausts_retry_budget() -> None:
    """Test active wrong-room cleaning cannot redispatch without a limit."""
    decision = _decision(
        vacuum_state="cleaning",
        expected_room_id=3,
        observed_room_id=1,
        expected_room_name="Dining Room",
        observed_room_name="Porch",
        cleaning_progress=50,
        active_room_mismatch_streak=3,
        active_room_mismatch_required_streak=2,
        dispatch_retry_count=2,
        dispatch_retry_max=2,
        seconds_since_last_command=120,
    )

    assert decision.retry_current_room is False
    assert decision.mark_out_of_sync_reason == (
        "active_room_mismatch_retry_exhausted:expected_3:observed_1"
    )
    assert decision.event_reasons == ("active_room_mismatch_retry_exhausted",)


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


def test_reconcile_unavailable_vacuum_waits_without_consuming_retry_budget() -> None:
    """Test missing robot observations cannot redispatch or exhaust retries."""
    decision = _decision(
        vacuum_state="",
        task_status="",
        seconds_since_last_command=300,
        dispatch_retry_count=2,
        dispatch_retry_max=2,
    )

    assert decision.retry_current_room is False
    assert decision.mark_out_of_sync_reason is None
    assert decision.reset_dispatch_retry_count is False
    assert decision.event_reasons == ("vacuum_unavailable_waiting",)


def test_reconcile_completed_task_survives_unavailable_vacuum_observation() -> None:
    """Test a valid completion remains authoritative during a vacuum outage."""
    decision = _decision(
        vacuum_state="",
        task_status="completed",
        task_status_cleared_since_dispatch=True,
        dispatch_retry_count=2,
        dispatch_retry_max=2,
    )

    assert decision.complete_current_room is True
    assert decision.retry_current_room is False
    assert decision.mark_out_of_sync_reason is None
    assert decision.event_reasons == ("task_status_completed",)


def test_reconcile_active_room_confirmation_resets_retry_budget() -> None:
    """Test a confirmed matching run clears retries from transient failures."""
    decision = _decision(
        vacuum_state="cleaning",
        task_status="room_cleaning",
        dispatch_retry_count=2,
        expected_room_id=1,
        observed_room_id=1,
    )

    assert decision.retry_current_room is False
    assert decision.mark_out_of_sync_reason is None
    assert decision.reset_dispatch_retry_count is True
    assert decision.set_active_room_confirmed_since_dispatch is True
    assert decision.event_reasons == ("dispatch_retry_reset_after_active_confirmation",)


def test_reconcile_active_state_without_room_confirmation_preserves_retry_budget() -> None:
    """Test missing room telemetry cannot repeatedly restore retry attempts."""
    decision = _decision(
        vacuum_state="cleaning",
        task_status="room_cleaning",
        dispatch_retry_count=1,
        expected_room_id=1,
        observed_room_id=None,
        observed_room_name=None,
    )

    assert decision.retry_current_room is False
    assert decision.reset_dispatch_retry_count is False
    assert decision.event_reasons == ()


def test_reconcile_active_room_mismatch_does_not_reset_retry_budget() -> None:
    """Test confirming the wrong active room cannot restore retry budget."""
    decision = _decision(
        vacuum_state="cleaning",
        task_status="room_cleaning",
        dispatch_retry_count=1,
        expected_room_id=1,
        observed_room_id=7,
        cleaning_progress=20,
        active_room_mismatch_streak=2,
        active_room_mismatch_required_streak=2,
        seconds_since_last_command=5,
    )

    assert decision.retry_current_room is False
    assert decision.reset_dispatch_retry_count is False
    assert decision.event_reasons == (
        "active_room_mismatch_waiting_retry_interval:expected_1:observed_7",
    )


def test_reconcile_dock_prep_preserves_retry_history_while_active() -> None:
    """Test ordinary dock preparation holds without claiming room confirmation."""
    decision = _decision(
        vacuum_state="docked",
        task_status="room_cleaning",
        is_dock_prep_state=True,
        seconds_since_last_command=300,
        dispatch_retry_count=2,
        dispatch_retry_max=2,
    )

    assert decision.retry_current_room is False
    assert decision.mark_out_of_sync_reason is None
    assert decision.reset_dispatch_retry_count is False
    assert decision.event_reasons == ()


def test_reconcile_post_run_maintenance_holds_without_resuming_or_retrying() -> None:
    """Test auto-emptying cannot resume, retry, or fail a completed robot run."""
    decision = _decision(
        vacuum_state="docked",
        task_status="room_cleaning",
        active_room_confirmed_since_dispatch=True,
        is_post_run_maintenance_state=True,
        is_dock_prep_paused=True,
        dock_prep_resume_ready=True,
        seconds_since_last_command=300,
        dispatch_retry_count=2,
        dispatch_retry_max=2,
    )

    assert decision.complete_current_room is False
    assert decision.retry_current_room is False
    assert decision.resume_current_room is False
    assert decision.mark_out_of_sync_reason is None
    assert decision.reset_dispatch_retry_count is True
    assert decision.set_post_run_maintenance_seen is True
    assert decision.event_reasons == ("post_run_maintenance_waiting",)


def test_reconcile_does_not_bind_stale_maintenance_to_unconfirmed_room() -> None:
    """Test prior-room auto-emptying cannot become sticky for a new queue item."""
    decision = _decision(
        vacuum_state="docked",
        task_status="completed",
        task_status_cleared_since_dispatch=False,
        active_room_confirmed_since_dispatch=False,
        is_post_run_maintenance_state=True,
        seconds_since_last_command=300,
        dispatch_retry_count=1,
        dispatch_retry_max=2,
    )

    assert decision.complete_current_room is False
    assert decision.retry_current_room is False
    assert decision.resume_current_room is False
    assert decision.mark_out_of_sync_reason is None
    assert decision.reset_dispatch_retry_count is False
    assert decision.set_post_run_maintenance_seen is False
    assert decision.event_reasons == (
        "task_status_completed_ignored_not_cleared_after_dispatch",
        "post_run_maintenance_waiting",
    )


def test_reconcile_remembers_post_run_maintenance_until_completion() -> None:
    """Test a plain docked state after auto-emptying cannot redispatch the room."""
    decision = _decision(
        vacuum_state="docked",
        task_status="room_cleaning",
        post_run_maintenance_seen=True,
        seconds_since_last_command=300,
        dispatch_retry_count=0,
        dispatch_retry_max=2,
    )

    assert decision.complete_current_room is False
    assert decision.retry_current_room is False
    assert decision.resume_current_room is False
    assert decision.mark_out_of_sync_reason is None
    assert decision.reset_dispatch_retry_count is False
    assert decision.event_reasons == ("post_run_completion_waiting",)

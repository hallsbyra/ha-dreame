"""Tests for pure reconciliation decisions."""

from datetime import UTC, datetime

import pytest

from custom_components.ha_dreame.queue_core import QueueItem
from custom_components.ha_dreame.reconcile_core import Decision, Observation, decide
from custom_components.ha_dreame.queue_core import DispatchTracking

NOW = datetime(2026, 5, 17, 8, 0, tzinfo=UTC)
TRACKING_FIELDS = (
    "task_status_cleared_since_dispatch",
    "dispatch_retry_count",
    "post_run_maintenance_seen",
    "active_room_confirmed_since_dispatch",
)


def _decision(**overrides: object) -> Decision:
    """Decide for an observation, the awaited room and its tracking given as flat values."""
    values: dict = {
        "vacuum_state": "cleaning",
        "task_status": "room_cleaning",
        "seconds_since_last_command": 5,
        "task_status_cleared_since_dispatch": True,
        "dispatch_retry_count": 0,
        "expected_room_id": 1,
        "observed_room_id": 1,
        "is_dock_prep_state": False,
    }
    values.update(overrides)
    item = QueueItem(
        item_id="item-1",
        room_id=values.pop("expected_room_id"),
        room_name=values.pop("expected_room_name", None) or "",
        status="running",
    )
    seconds = values.pop("seconds_since_last_command")
    tracking = DispatchTracking(
        last_command_at=NOW,
        **{key: values.pop(key) for key in TRACKING_FIELDS if key in values},
    )
    return decide(Observation(**values), item, tracking, seconds)


def test_reconcile_sets_task_status_cleared_after_dispatch() -> None:
    """Test non-completed task status enables later completion."""
    decision = _decision(task_status_cleared_since_dispatch=False)

    assert decision.tracking.task_status_cleared_since_dispatch is True
    assert decision.action != "complete"
    assert decision.action != "retry"
    assert decision.reasons == ("task_status_cleared_after_dispatch",)


def test_reconcile_stale_completed_status_does_not_complete_room() -> None:
    """Test stale completed task status after dispatch is ignored."""
    decision = _decision(
        vacuum_state="idle",
        task_status="completed",
        task_status_cleared_since_dispatch=False,
        seconds_since_last_command=10,
    )

    assert decision.action != "complete"
    assert decision.action != "retry"
    assert decision.fail_reason is None
    assert decision.reasons == ("task_status_completed_ignored_not_cleared_after_dispatch",)


def test_reconcile_completed_after_status_cleared_completes_room() -> None:
    """Test completed status can complete only after task status was cleared."""
    decision = _decision(
        vacuum_state="idle",
        task_status="completed",
        task_status_cleared_since_dispatch=True,
        seconds_since_last_command=30,
    )

    assert decision.action == "complete"
    assert decision.action != "retry"
    assert decision.fail_reason is None
    assert decision.reasons == ("task_status_completed",)


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
        seconds_since_last_command=30,
    )

    assert decision.action != "complete"
    assert decision.action != "retry"
    assert decision.fail_reason == ("task_completed_unconfirmed_room:expected_3:observed_1")
    assert decision.reasons == ("task_status_completed_unconfirmed_room",)


def test_reconcile_completed_unconfirmed_wrong_room_right_after_dispatch_waits() -> None:
    """Test a reconnect replay of the previous task's completion cannot end a fresh dispatch."""
    decision = _decision(
        vacuum_state="docked",
        task_status="completed",
        task_status_cleared_since_dispatch=True,
        expected_room_id=3,
        observed_room_id=7,
        expected_room_name="Dining Room",
        observed_room_name="Hall",
        active_room_confirmed_since_dispatch=False,
        seconds_since_last_command=3,
    )

    assert decision.action != "complete"
    assert decision.action != "retry"
    assert decision.fail_reason is None
    assert decision.reasons == ("task_status_completed_unconfirmed_room_waiting",)


def test_reconcile_unconfirmed_completion_with_unknown_room_right_after_dispatch_waits() -> None:
    """Test a replayed completion cannot end a fresh dispatch while the room sensor is missing."""
    decision = _decision(
        vacuum_state="docked",
        task_status="completed",
        task_status_cleared_since_dispatch=True,
        observed_room_id=None,
        active_room_confirmed_since_dispatch=False,
        seconds_since_last_command=3,
    )

    assert decision.action != "complete"
    assert decision.fail_reason is None
    assert decision.reasons == ("task_status_completed_unconfirmed_room_waiting",)


def test_reconcile_unconfirmed_completion_with_unknown_room_completes_after_interval() -> None:
    """Test installs without a room signal can still complete rooms."""
    decision = _decision(
        vacuum_state="docked",
        task_status="completed",
        task_status_cleared_since_dispatch=True,
        observed_room_id=None,
        active_room_confirmed_since_dispatch=False,
        seconds_since_last_command=30,
    )

    assert decision.action == "complete"


@pytest.mark.parametrize("cleaning_progress", [None, 3, 40])
def test_reconcile_room_flip_after_confirmation_never_redispatches(
    cleaning_progress: int | None,
) -> None:
    """Test a confirmed room is not redispatched when the room sensor flips mid-run."""
    decision = _decision(
        vacuum_state="cleaning",
        task_status="room_cleaning",
        expected_room_id=3,
        observed_room_id=4,
        active_room_confirmed_since_dispatch=True,
        cleaning_progress=cleaning_progress,
        seconds_since_last_command=300,
    )

    assert decision.action != "retry"
    assert decision.fail_reason is None
    assert decision.reasons == ("active_room_mismatch_after_confirmation:expected_3:observed_4",)


def test_reconcile_stale_completed_status_retries_after_interval() -> None:
    """Test stale completed status falls through to retry recovery."""
    decision = _decision(
        vacuum_state="idle",
        task_status="completed",
        task_status_cleared_since_dispatch=False,
        seconds_since_last_command=30,
    )

    assert decision.action != "complete"
    assert decision.action == "retry"
    assert decision.fail_reason is None
    assert decision.reasons == (
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
        expected_room_id=1,
        observed_room_id=7,
    )

    assert decision.action != "complete"
    assert decision.action != "retry"
    assert decision.fail_reason == ("dispatch_retry_exhausted:expected_1:observed_7:vacuum_idle")
    assert decision.reasons == (
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

    assert decision.action != "complete"
    assert decision.action != "retry"
    assert decision.fail_reason is None
    assert decision.reasons == ("task_status_completed_ignored_not_cleared_after_dispatch",)


def test_reconcile_route_error_marks_blocked() -> None:
    """Test route errors become terminal blocked decisions."""
    decision = _decision(
        vacuum_state="error",
        task_status="completed",
        vacuum_error_code="route",
        expected_room_id=1,
        observed_room_id=7,
    )

    assert decision.action != "complete"
    assert decision.action != "retry"
    assert decision.action == "fail"
    assert decision.blocked is True
    assert decision.fail_reason == "vacuum_route_error:expected_1:observed_7"
    assert decision.reasons == ("vacuum_error_route_blocked",)


def test_reconcile_error_state_ignores_completed_status() -> None:
    """Test completed status does not complete while vacuum is in error."""
    decision = _decision(
        vacuum_state="error",
        task_status="completed",
        vacuum_error_code="water_tank_dry",
        task_status_cleared_since_dispatch=True,
        seconds_since_last_command=120,
    )

    assert decision.action != "complete"
    assert decision.action != "retry"
    assert decision.fail_reason is None
    assert decision.tracking.dispatch_retry_count == 0
    assert decision.reasons == (
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

    assert decision.action != "complete"
    assert decision.action != "retry"
    assert decision.fail_reason is None
    assert decision.tracking.dispatch_retry_count == 0
    assert decision.reasons == (
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

    assert decision.action != "complete"
    assert decision.action != "retry"
    assert decision.fail_reason is None
    assert decision.tracking.dispatch_retry_count == 0
    assert decision.reasons == ("vacuum_error_waiting_user_action",)


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

    assert decision.action != "retry"
    assert decision.action != "resume"
    assert decision.fail_reason is None
    assert decision.reasons == ("dock_prep_paused_waiting_resume_ready",)


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

    assert decision.action != "retry"
    assert decision.action != "resume"
    assert decision.tracking.dispatch_retry_count == 0
    assert decision.reasons == ("vacuum_error_waiting_user_action",)


def test_reconcile_dock_prep_pause_waits_for_retry_interval() -> None:
    """Test dock-prep resume waits for the retry interval."""
    decision = _decision(
        vacuum_state="cleaning",
        task_status="room_cleaning",
        is_dock_prep_state=True,
        is_dock_prep_paused=True,
        dock_prep_resume_ready=True,
        seconds_since_last_command=10,
    )

    assert decision.action != "retry"
    assert decision.action != "resume"
    assert decision.reasons == ("dock_prep_paused_waiting_retry_interval",)


def test_reconcile_mop_remove_transition_waits_without_retry_or_out_of_sync() -> None:
    """Test mop removal maintenance does not consume dispatch retry budget."""
    decision = _decision(
        vacuum_state="docked",
        task_status="returning_to_remove_mop",
        is_mop_maintenance_state=True,
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
    )

    assert decision.action != "complete"
    assert decision.action != "retry"
    assert decision.fail_reason is None
    assert decision.tracking.dispatch_retry_count == 2
    assert decision.reasons == ("mop_maintenance_waiting",)


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
        is_dock_prep_state=False,
        is_mop_maintenance_state=True,
    )

    assert decision.action != "complete"
    assert decision.action != "retry"
    assert decision.fail_reason is None
    assert decision.reasons == ("mop_maintenance_waiting",)


def test_reconcile_dock_prep_pause_requests_resume_when_ready() -> None:
    """Test dock-prep pause asks runtime layer to resume once safe."""
    decision = _decision(
        vacuum_state="cleaning",
        task_status="room_cleaning",
        is_dock_prep_state=True,
        is_dock_prep_paused=True,
        dock_prep_resume_ready=True,
        seconds_since_last_command=120,
    )

    assert decision.action != "retry"
    assert decision.action == "resume"
    assert decision.reasons == ("dock_prep_paused_resume_requested",)


def test_reconcile_paused_robot_waits_without_retry() -> None:
    """Test paused robot/task states are treated as hold states."""
    decision = _decision(
        vacuum_state="paused",
        task_status="room_cleaning_paused",
        seconds_since_last_command=120,
    )

    assert decision.action != "retry"
    assert decision.fail_reason is None
    assert decision.reasons == ("vacuum_paused_waiting",)


def test_reconcile_paused_robot_with_blocking_error_waits_for_user_action() -> None:
    """Test paused robot with an error stays in recoverable hold."""
    decision = _decision(
        vacuum_state="paused",
        task_status="room_cleaning_paused",
        vacuum_error_code="water_tank_dry",
        seconds_since_last_command=120,
    )

    assert decision.action != "retry"
    assert decision.fail_reason is None
    assert decision.tracking.dispatch_retry_count == 0
    assert decision.reasons == ("vacuum_error_waiting_user_action",)


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

    assert decision.action != "retry"
    assert decision.fail_reason is None
    assert not any(reason.startswith("active_room_mismatch") for reason in decision.reasons)


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

    assert decision.action == "retry"
    assert any(reason.startswith("active_room_mismatch_retry:") for reason in decision.reasons)


def test_reconcile_early_room_mismatch_waits_for_min_progress() -> None:
    """Test early room mismatch is treated as transition noise."""
    decision = _decision(
        vacuum_state="cleaning",
        observed_room_id=7,
        expected_room_name="Kitchen",
        observed_room_name="Hall",
        cleaning_progress=0,
        seconds_since_last_command=120,
    )

    assert decision.action != "retry"
    assert any(
        reason.startswith("active_room_mismatch_waiting_progress:") for reason in decision.reasons
    )


def test_reconcile_unconfirmed_late_room_mismatch_marks_out_of_sync() -> None:
    """Test an unconfirmed wrong-room run cannot hide behind high progress."""
    decision = _decision(
        vacuum_state="cleaning",
        observed_room_id=7,
        expected_room_name="Kitchen",
        observed_room_name="Hall",
        cleaning_progress=95,
        active_room_confirmed_since_dispatch=False,
        seconds_since_last_command=120,
    )

    assert decision.action != "retry"
    assert decision.fail_reason == (
        "active_room_mismatch_unconfirmed_near_completion:expected_1:observed_7"
    )
    assert decision.reasons == (
        "active_room_mismatch_unconfirmed_near_completion:expected_1:observed_7:progress_95:max_90",
    )


def test_reconcile_confirmed_late_room_mismatch_waits_near_completion() -> None:
    """Test a late room flip is tolerated after the target room was confirmed."""
    decision = _decision(
        vacuum_state="cleaning",
        expected_room_name="Kitchen",
        observed_room_name="Hall",
        cleaning_progress=95,
        active_room_confirmed_since_dispatch=True,
        seconds_since_last_command=120,
    )

    assert decision.action != "retry"
    assert decision.fail_reason is None
    assert decision.reasons == ("active_room_mismatch_after_confirmation:expected_1:observed_1",)


def test_reconcile_room_mismatch_waits_for_retry_interval() -> None:
    """Test room mismatch retry waits for command retry interval."""
    decision = _decision(
        vacuum_state="cleaning",
        expected_room_name="Kitchen",
        observed_room_name="Hall",
        cleaning_progress=20,
        seconds_since_last_command=5,
    )

    assert decision.action != "retry"
    assert any(
        reason.startswith("active_room_mismatch_waiting_retry_interval:")
        for reason in decision.reasons
    )


def test_reconcile_room_mismatch_retries_after_interval() -> None:
    """Test sustained room mismatch requests a retry."""
    decision = _decision(
        vacuum_state="cleaning",
        expected_room_name="Kitchen",
        observed_room_name="Hall",
        cleaning_progress=20,
        dispatch_retry_count=1,
        seconds_since_last_command=120,
    )

    assert decision.action == "retry"
    assert decision.fail_reason is None
    assert any(reason.startswith("active_room_mismatch_retry:2:") for reason in decision.reasons)


def test_reconcile_room_mismatch_exhausts_retry_budget() -> None:
    """Test active wrong-room cleaning cannot redispatch without a limit."""
    decision = _decision(
        vacuum_state="cleaning",
        expected_room_id=3,
        observed_room_id=1,
        expected_room_name="Dining Room",
        observed_room_name="Porch",
        cleaning_progress=50,
        dispatch_retry_count=2,
        seconds_since_last_command=120,
    )

    assert decision.action != "retry"
    assert decision.fail_reason == ("active_room_mismatch_retry_exhausted:expected_3:observed_1")
    assert decision.reasons == ("active_room_mismatch_retry_exhausted",)


def test_reconcile_non_active_state_retries_after_interval() -> None:
    """Test non-active robot state triggers redispatch after the retry interval."""
    decision = _decision(
        vacuum_state="idle",
        task_status="room_cleaning",
        seconds_since_last_command=30,
        dispatch_retry_count=0,
    )

    assert decision.action == "retry"
    assert decision.tracking.dispatch_retry_count == 1
    assert decision.fail_reason is None
    assert decision.reasons == ("retry_dispatch_requested:1",)


def test_reconcile_non_active_state_escalates_after_retry_budget() -> None:
    """Test retry budget exhaustion escalates to out_of_sync."""
    decision = _decision(
        vacuum_state="idle",
        task_status="room_cleaning",
        seconds_since_last_command=30,
        dispatch_retry_count=2,
        expected_room_id=1,
        observed_room_id=7,
    )

    assert decision.action != "retry"
    assert decision.fail_reason == ("dispatch_retry_exhausted:expected_1:observed_7:vacuum_idle")
    assert decision.action == "fail"
    assert decision.blocked is False
    assert decision.reasons == ("dispatch_retry_exhausted",)


def test_reconcile_unavailable_vacuum_waits_without_consuming_retry_budget() -> None:
    """Test missing robot observations cannot redispatch or exhaust retries."""
    decision = _decision(
        vacuum_state="",
        task_status="",
        seconds_since_last_command=300,
        dispatch_retry_count=2,
    )

    assert decision.action != "retry"
    assert decision.fail_reason is None
    assert decision.tracking.dispatch_retry_count == 2
    assert decision.reasons == ("vacuum_unavailable_waiting",)


def test_reconcile_completed_task_survives_unavailable_vacuum_observation() -> None:
    """Test a valid completion remains authoritative during a vacuum outage."""
    decision = _decision(
        vacuum_state="",
        task_status="completed",
        task_status_cleared_since_dispatch=True,
        dispatch_retry_count=2,
        seconds_since_last_command=120,
    )

    assert decision.action == "complete"
    assert decision.action != "retry"
    assert decision.fail_reason is None
    assert decision.reasons == ("task_status_completed",)


def test_reconcile_active_room_confirmation_resets_retry_budget() -> None:
    """Test a confirmed matching run clears retries from transient failures."""
    decision = _decision(
        vacuum_state="cleaning",
        task_status="room_cleaning",
        dispatch_retry_count=2,
        expected_room_id=1,
        observed_room_id=1,
    )

    assert decision.action != "retry"
    assert decision.fail_reason is None
    assert decision.tracking.dispatch_retry_count == 0
    assert decision.tracking.active_room_confirmed_since_dispatch is True
    assert decision.reasons == ("dispatch_retry_reset_after_active_confirmation",)


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

    assert decision.action != "retry"
    assert decision.tracking.dispatch_retry_count == 1
    assert decision.reasons == ()


def test_reconcile_active_room_mismatch_does_not_reset_retry_budget() -> None:
    """Test confirming the wrong active room cannot restore retry budget."""
    decision = _decision(
        vacuum_state="cleaning",
        task_status="room_cleaning",
        dispatch_retry_count=1,
        expected_room_id=1,
        observed_room_id=7,
        cleaning_progress=20,
        seconds_since_last_command=5,
    )

    assert decision.action != "retry"
    assert decision.tracking.dispatch_retry_count == 1
    assert decision.reasons == (
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
    )

    assert decision.action != "retry"
    assert decision.fail_reason is None
    assert decision.tracking.dispatch_retry_count == 2
    assert decision.reasons == ()


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
    )

    assert decision.action != "complete"
    assert decision.action != "retry"
    assert decision.action != "resume"
    assert decision.fail_reason is None
    assert decision.tracking.dispatch_retry_count == 0
    assert decision.tracking.post_run_maintenance_seen is True
    assert decision.reasons == ("post_run_maintenance_waiting",)


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
    )

    assert decision.action != "complete"
    assert decision.action != "retry"
    assert decision.action != "resume"
    assert decision.fail_reason is None
    assert decision.tracking.dispatch_retry_count == 1
    assert decision.tracking.post_run_maintenance_seen is False
    assert decision.reasons == (
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
    )

    assert decision.action != "complete"
    assert decision.action != "retry"
    assert decision.action != "resume"
    assert decision.fail_reason is None
    assert decision.tracking.dispatch_retry_count == 0
    assert decision.reasons == ("post_run_completion_waiting",)


def test_reconcile_paused_robot_is_paused_unless_in_error() -> None:
    """Test pause evidence beyond the vacuum state holds the room as paused."""
    decision = _decision(vacuum_state="cleaning", robot_paused=True, seconds_since_last_command=300)

    assert decision.action == "hold"
    assert decision.reasons == ("vacuum_paused_waiting",)

    decision = _decision(vacuum_state="error", robot_paused=True, vacuum_error_code="route")

    assert decision.action == "fail"
    assert decision.blocked is True


def test_paused_drying_never_automatically_resumes_after_tank_recovery() -> None:
    """Test paused drying is not resumable dock preparation, even when refill is ready."""
    decision = _decision(
        vacuum_state="docked",
        task_status="room_cleaning",
        robot_paused=True,
        is_drying_state=True,
        is_dock_prep_state=True,
        is_dock_prep_paused=True,
        dock_prep_resume_ready=True,
        seconds_since_last_command=600,
    )

    assert decision.action == "hold"
    assert "vacuum_paused_waiting" in decision.reasons


def test_dirty_tank_blocks_automatic_dispatch_retry() -> None:
    """Test a tank problem holds instead of redispatching after the retry interval."""
    decision = _decision(
        vacuum_state="idle",
        task_status="room_cleaning",
        water_tank_block_reason="dirty_water_tank_not_ready",
        seconds_since_last_command=600,
    )

    assert decision.action == "hold"
    assert decision.reasons == ("dirty_water_tank_not_ready",)

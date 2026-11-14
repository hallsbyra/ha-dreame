"""Tests for the one place that decides which queue actions the user may take now."""

from dataclasses import replace
from datetime import datetime

import pytest

from custom_components.ha_dreame.control_core import (
    QUEUE_ACTIONS,
    ControlState,
    control_state,
    start_readiness,
)
from custom_components.ha_dreame.queue_core import (
    DispatchTracking,
    QueueState,
    add_room,
    external_takeover,
    start_run,
)
from custom_components.ha_dreame.reconcile_core import Observation

START = "start_queue"
RESUME = "resume_queue"
SKIP = "skip_current_room"
CANCEL = "cancel_queue"
READY = Observation(vacuum_state="docked", task_status="completed", vacuum_error_code="no_error")
TANK = replace(READY, vacuum_state="error", water_tank_block_reason="clean_water_tank_not_ready")
CLEANING = Observation(vacuum_state="cleaning", task_status="room_cleaning")


def _pending() -> QueueState:
    return add_room(QueueState(), room_id=1, room_name="Kitchen")


def _running() -> QueueState:
    state = start_run(add_room(_pending(), room_id=2, room_name="Hall"))
    return replace(
        state,
        dispatch=DispatchTracking(last_command_at=datetime.fromisoformat("2026-01-01T00:00Z")),
    )


def _decide(
    queue_state: QueueState, observation: Observation, *, commands: bool = True
) -> ControlState:
    return control_state(queue_state, observation, commands)


def test_every_queue_action_is_either_allowed_or_blocked_with_a_reason() -> None:
    state = _decide(_running(), CLEANING)

    assert set(QUEUE_ACTIONS) == {START, RESUME, SKIP, CANCEL}
    for action in QUEUE_ACTIONS:
        assert (action in state.allowed_actions) != (action in state.blocked_reasons)
    assert state.allows(SKIP)
    assert state.reason(SKIP) is None
    assert state.reason(START) == "run_active"


def test_ready_robot_with_pending_rooms_may_start() -> None:
    state = _decide(_pending(), READY)

    assert state.allowed_actions == (START, CANCEL)
    assert state.blocked_reasons == {
        RESUME: "not_running",
        SKIP: "not_running",
    }


def test_empty_queue_cannot_start() -> None:
    assert _decide(QueueState(), READY).reason(START) == "queue_empty"


def test_closed_command_gate_blocks_every_robot_action() -> None:
    assert _decide(_pending(), READY, commands=False).reason(START) == "commands_disabled"
    running = _decide(_running(), Observation(vacuum_state="paused"), commands=False)
    assert running.allowed_actions == ()
    assert running.reason(RESUME) == "commands_disabled"
    assert running.reason(SKIP) == "commands_disabled"
    assert running.reason(CANCEL) == "commands_disabled"


@pytest.mark.parametrize(
    "observation",
    [
        Observation(task_status="completed"),
        Observation(vacuum_state="unavailable", task_status="completed"),
        replace(TANK, vacuum_state=""),
    ],
)
def test_unavailable_robot_cannot_start_with_or_without_a_tank_problem(
    observation: Observation,
) -> None:
    """The vacuum must be available for any start, not only for a tank-blocked one."""
    assert _decide(_pending(), observation).reason(START) == "robot_unavailable"


@pytest.mark.parametrize(
    "observation",
    [
        replace(READY, task_status="room_cleaning"),
        replace(READY, vacuum_state="returning", task_status="room_cleaning"),
        replace(READY, vacuum_state="returning"),
        replace(READY, vacuum_state="cleaning"),
        replace(READY, vacuum_state="paused"),
        replace(READY, robot_paused=True),
        replace(TANK, task_status="room_cleaning_paused"),
    ],
)
def test_busy_robot_rejects_start(observation: Observation) -> None:
    """A previous task must settle first, even when a tank problem would arm a wait."""
    assert _decide(_pending(), observation).reason(START) == "robot_busy"


@pytest.mark.parametrize(
    "observation",
    [replace(READY, vacuum_state="error"), replace(READY, vacuum_error_code="route")],
)
def test_robot_error_rejects_start(observation: Observation) -> None:
    assert _decide(_pending(), observation).reason(START) == "robot_error"


@pytest.mark.parametrize(
    "observation",
    [TANK, replace(TANK, vacuum_state="docked", robot_paused=True)],
)
def test_tank_problem_lets_start_arm_a_waiting_start(observation: Observation) -> None:
    assert _decide(_pending(), observation).allows(START)
    assert start_readiness(observation) == "tank_attention"


def test_absent_task_status_counts_as_no_active_task() -> None:
    """Start and the waiting-start release treat a missing task status alike."""
    observation = replace(READY, task_status="")

    assert start_readiness(observation) is None
    assert _decide(_pending(), observation).allows(START)


def test_start_readiness_reports_a_robot_ready_for_dispatch() -> None:
    assert start_readiness(READY) is None
    assert start_readiness(replace(READY, vacuum_state="idle")) is None


def test_waiting_start_can_always_be_canceled() -> None:
    """Canceling a waiting start sends no robot command, so the command gate does not apply."""
    waiting = replace(_pending(), run_state="waiting_for_tanks")

    disabled = _decide(waiting, TANK, commands=False)
    assert disabled.allowed_actions == (CANCEL,)
    assert disabled.reason(START) == "commands_disabled"
    assert disabled.reason(RESUME) == "not_running"
    assert disabled.reason(SKIP) == "not_running"


def test_repeated_start_while_waiting_follows_the_normal_start_rules() -> None:
    """Pressing Start again keeps waiting, or dispatches at once if the robot is ready."""
    waiting = replace(_pending(), run_state="waiting_for_tanks")

    assert _decide(waiting, TANK).allowed_actions == (START, CANCEL)
    assert _decide(waiting, READY).allowed_actions == (START, CANCEL)
    assert _decide(waiting, replace(TANK, task_status="room_cleaning")).reason(START) == (
        "robot_busy"
    )


def test_running_queue_offers_skip_and_cancel_while_the_robot_works() -> None:
    state = _decide(_running(), CLEANING)

    assert state.allowed_actions == (SKIP, CANCEL)
    assert state.blocked_reasons == {START: "run_active", RESUME: "not_interrupted"}


@pytest.mark.parametrize(
    "observation",
    [
        Observation(vacuum_state="paused", task_status="room_cleaning_paused"),
        Observation(vacuum_state="error", task_status="room_cleaning", vacuum_error_code="mop"),
        Observation(vacuum_state="docked", task_status="room_cleaning", robot_paused=True),
    ],
)
def test_interrupted_run_may_resume(observation: Observation) -> None:
    state = _decide(_running(), observation)

    assert state.allowed_actions == (RESUME, SKIP, CANCEL)


def test_tank_problem_blocks_resume_but_not_cancel() -> None:
    observation = Observation(
        vacuum_state="docked",
        task_status="room_cleaning",
        robot_paused=True,
        water_tank_block_reason="dirty_water_tank_not_ready",
    )
    state = _decide(_running(), observation)

    assert state.reason(RESUME) == "tank_attention"
    assert state.allows(CANCEL)


def test_unavailable_robot_cannot_resume() -> None:
    state = _decide(_running(), Observation(robot_paused=True))

    assert state.reason(RESUME) == "robot_unavailable"
    assert state.allows(CANCEL)


def test_run_without_dispatch_tracking_cannot_resume() -> None:
    state = _decide(replace(_running(), dispatch=None), Observation(vacuum_state="paused"))

    assert state.reason(RESUME) == "not_running"


@pytest.mark.parametrize("run_state", ["completed", "canceled"])
def test_finished_queue_without_pending_rooms_offers_only_cancel(run_state: str) -> None:
    state = _decide(replace(QueueState(), run_state=run_state), READY)

    assert state.allowed_actions == (CANCEL,)
    assert state.reason(START) == "queue_empty"


@pytest.mark.parametrize("blocked", [True, False])
def test_failed_run_with_remaining_rooms_may_run_them_under_the_start_rules(
    blocked: bool,
) -> None:
    failed = external_takeover(_running(), reason="stopped_from_app", blocked=blocked)

    assert _decide(failed, READY).allowed_actions == (START, CANCEL)
    assert _decide(failed, TANK).allows(START)
    assert _decide(failed, replace(READY, task_status="room_cleaning")).reason(START) == (
        "robot_busy"
    )
    assert _decide(failed, READY, commands=False).reason(START) == "commands_disabled"


def test_failed_run_without_remaining_rooms_cannot_start() -> None:
    failed = external_takeover(start_run(_pending()), reason="stopped_from_app")

    assert _decide(failed, READY).reason(START) == "queue_empty"

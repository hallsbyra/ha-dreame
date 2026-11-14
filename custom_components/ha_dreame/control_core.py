"""Pure decision of which queue actions the user may take now.

Services check it before acting, get_control_readiness returns it, the queue status
sensor publishes it and the card renders it. docs/dreame-behavior-knowledge.md records
the robot behavior behind each rule.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from .const import (
    SERVICE_CANCEL_QUEUE,
    SERVICE_RESUME_QUEUE,
    SERVICE_SKIP_CURRENT_ROOM,
    SERVICE_START_QUEUE,
)
from .queue_core import QueueState
from .reconcile_core import Observation, is_meaningful_error

QUEUE_ACTIONS = (
    SERVICE_START_QUEUE,
    SERVICE_RESUME_QUEUE,
    SERVICE_SKIP_CURRENT_ROOM,
    SERVICE_CANCEL_QUEUE,
)

COMMANDS_DISABLED = "commands_disabled"
ROBOT_UNAVAILABLE = "robot_unavailable"
ROBOT_BUSY = "robot_busy"
ROBOT_ERROR = "robot_error"
TANK_ATTENTION = "tank_attention"
QUEUE_EMPTY = "queue_empty"
RUN_ACTIVE = "run_active"
NOT_RUNNING = "not_running"
NOT_INTERRUPTED = "not_interrupted"
# Reasons that say the action does not apply to the queue's current phase, rather than
# that something blocks it.
INAPPLICABLE_REASONS = frozenset({RUN_ACTIVE, NOT_RUNNING, NOT_INTERRUPTED})

_ABSENT_VACUUM_STATES = frozenset({"", "unknown", "unavailable"})
_BUSY_VACUUM_STATES = frozenset({"cleaning", "returning"})
_IDLE_TASK_STATUSES = frozenset({"", "completed"})


@dataclass(frozen=True, slots=True)
class ControlState:
    """Each queue action is either allowed now or blocked with a reason code."""

    allowed_actions: tuple[str, ...] = ()
    blocked_reasons: Mapping[str, str] = field(default_factory=dict)

    def allows(self, action: str) -> bool:
        """Return whether the action is allowed now."""
        return action in self.allowed_actions

    def reason(self, action: str) -> str | None:
        """Return why the action is blocked, or None when it is allowed."""
        return self.blocked_reasons.get(action)


def control_state(
    queue_state: QueueState,
    observation: Observation,
    commands_enabled: bool,
) -> ControlState:
    """Decide which queue actions the user may take for this queue and robot."""
    reasons = {
        SERVICE_START_QUEUE: _start_reason(queue_state, observation, commands_enabled),
        SERVICE_RESUME_QUEUE: _resume_reason(queue_state, observation, commands_enabled),
        SERVICE_SKIP_CURRENT_ROOM: _skip_reason(queue_state, commands_enabled),
        SERVICE_CANCEL_QUEUE: _cancel_reason(queue_state, commands_enabled),
    }
    return ControlState(
        allowed_actions=tuple(action for action in QUEUE_ACTIONS if reasons[action] is None),
        blocked_reasons={
            action: reason for action, reason in reasons.items() if reason is not None
        },
    )


def start_readiness(observation: Observation) -> str | None:
    """Return None when the robot can take a room now, else why not.

    `TANK_ATTENTION` means Start is accepted as a waiting start that the automatic
    reconcile releases once this returns None. Any other reason blocks Start.
    """
    vacuum = _normalize(observation.vacuum_state)
    if vacuum in _ABSENT_VACUUM_STATES:
        return ROBOT_UNAVAILABLE
    if (
        _normalize(observation.task_status) not in _IDLE_TASK_STATUSES
        or vacuum in _BUSY_VACUUM_STATES
    ):
        return ROBOT_BUSY
    if observation.water_tank_block_reason:
        return TANK_ATTENTION
    if vacuum == "paused" or observation.robot_paused:
        return ROBOT_BUSY
    if vacuum == "error" or is_meaningful_error(_normalize(observation.vacuum_error_code)):
        return ROBOT_ERROR
    return None


def robot_status(observation: Observation) -> dict[str, Any]:
    """Return why the robot interrupted its run, from read-only companion entities."""
    vacuum_state = _normalize(observation.vacuum_state)
    task_status = _normalize(observation.task_status)
    error_code = _normalize(observation.vacuum_error_code)

    interruption_reasons: list[str] = []
    if vacuum_state == "paused":
        interruption_reasons.append("vacuum_paused")
    elif observation.robot_paused:
        interruption_reasons.append("robot_paused")
    if observation.water_tank_block_reason:
        interruption_reasons.append(observation.water_tank_block_reason)
    if task_status.endswith("_paused"):
        interruption_reasons.append("task_status_paused")
    interruption_context = bool(interruption_reasons) or vacuum_state == "error"
    if vacuum_state == "error":
        interruption_reasons.append(
            f"vacuum_error:{error_code}" if is_meaningful_error(error_code) else "vacuum_error"
        )
    elif interruption_context and is_meaningful_error(error_code):
        interruption_reasons.append(f"vacuum_error:{error_code}")

    return {
        "error_code": error_code,
        "interruption_reasons": interruption_reasons,
        "interrupted": bool(interruption_reasons),
        "task_status": task_status,
        "vacuum_state": vacuum_state,
    }


def _start_reason(
    queue_state: QueueState, observation: Observation, commands_enabled: bool
) -> str | None:
    if queue_state.run_state == "running":
        return RUN_ACTIVE
    if not any(item.status == "pending" for item in queue_state.items):
        return QUEUE_EMPTY
    if not commands_enabled:
        return COMMANDS_DISABLED
    readiness = start_readiness(observation)
    return None if readiness == TANK_ATTENTION else readiness


def _resume_reason(
    queue_state: QueueState, observation: Observation, commands_enabled: bool
) -> str | None:
    if queue_state.run_state != "running" or queue_state.dispatch is None:
        return NOT_RUNNING
    if not commands_enabled:
        return COMMANDS_DISABLED
    if _normalize(observation.vacuum_state) in _ABSENT_VACUUM_STATES:
        return ROBOT_UNAVAILABLE
    if observation.water_tank_block_reason:
        return TANK_ATTENTION
    if not robot_status(observation)["interrupted"]:
        return NOT_INTERRUPTED
    return None


def _skip_reason(queue_state: QueueState, commands_enabled: bool) -> str | None:
    if queue_state.run_state != "running":
        return NOT_RUNNING
    if not commands_enabled:
        return COMMANDS_DISABLED
    return None


def _cancel_reason(queue_state: QueueState, commands_enabled: bool) -> str | None:
    # Canceling a waiting start sends no robot command, so the command gate does not apply.
    if queue_state.run_state == "waiting_for_tanks":
        return None
    return _skip_reason(queue_state, commands_enabled)


def _normalize(value: str | None) -> str:
    return (value or "").strip().lower()

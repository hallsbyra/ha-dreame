"""Pure reconcile decisions for the queue room the robot was last sent to.

docs/dreame-behavior-knowledge.md records the observed robot behavior behind each rule.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Literal

from .queue_core import DispatchTracking, QueueItem

ACTIVE_STATES = frozenset({"cleaning", "returning"})
DISPATCH_RETRY_INTERVAL_SEC = 20
DISPATCH_RETRY_MAX = 2
ACTIVE_ROOM_MISMATCH_MIN_PROGRESS = 1
ACTIVE_ROOM_MISMATCH_MAX_PROGRESS = 90
NO_ERROR_CODES = frozenset({"", "unknown", "unavailable", "no_error"})
VACUUM_ERROR_WAIT_REASON = "vacuum_error_waiting_user_action"

Action = Literal["hold", "complete", "retry", "resume", "fail"]


@dataclass(frozen=True, slots=True)
class Observation:
    """One public-safe robot observation."""

    vacuum_state: str = ""
    task_status: str = ""
    vacuum_error_code: str = ""
    robot_paused: bool = False
    is_drying_state: bool = False
    water_tank_block_reason: str = ""
    observed_room_id: int | None = None
    observed_room_name: str | None = None
    cleaning_progress: int | None = None
    is_dock_prep_state: bool = False
    is_dock_prep_paused: bool = False
    dock_prep_resume_ready: bool = False
    is_mop_maintenance_state: bool = False
    is_post_run_maintenance_state: bool = False


@dataclass(frozen=True, slots=True)
class Decision:
    """What to do about the awaited room, and the run tracking to keep for it.

    A retry carries the incremented retry count to dispatch with. A failed run is
    `blocked` when the robot reported that it cannot reach the room, else out of sync.
    """

    action: Action
    tracking: DispatchTracking
    reasons: tuple[str, ...] = ()
    fail_reason: str | None = None
    blocked: bool = False


def is_meaningful_error(error_code: str) -> bool:
    """Return whether a normalized Dreame error code is an actionable robot error."""
    return error_code not in NO_ERROR_CODES


def decide(
    observation: Observation,
    item: QueueItem,
    tracking: DispatchTracking,
    seconds_since_command: float,
) -> Decision:
    """Decide one tick while `item` awaits completion under `tracking`."""
    vacuum = _normalize(observation.vacuum_state)
    if observation.robot_paused and vacuum != "error":
        vacuum = "paused"
    task = _normalize(observation.task_status)
    error = _normalize(observation.vacuum_error_code)
    expected_observed = f"expected_{item.room_id}:observed_{observation.observed_room_id}"
    reasons: list[str] = []

    if task not in {"", "unknown", "unavailable", "completed"}:
        if not tracking.task_status_cleared_since_dispatch:
            tracking = replace(tracking, task_status_cleared_since_dispatch=True)
            reasons.append("task_status_cleared_after_dispatch")

    def hold(*extra: str, **changes: Any) -> Decision:
        return Decision("hold", replace(tracking, **changes), (*reasons, *extra))

    def fail(fail_reason: str, extra: str, *, blocked: bool = False) -> Decision:
        return Decision("fail", tracking, (*reasons, extra), fail_reason, blocked)

    def retry(extra: str) -> Decision:
        retry_count = tracking.dispatch_retry_count + 1
        return Decision(
            "retry", replace(tracking, dispatch_retry_count=retry_count), (*reasons, extra)
        )

    def wait_for_user_action() -> Decision:
        return hold(VACUUM_ERROR_WAIT_REASON, dispatch_retry_count=0)

    if vacuum == "error":
        if error == "route":
            return fail(
                f"vacuum_route_error:{expected_observed}",
                "vacuum_error_route_blocked",
                blocked=True,
            )
        if task == "completed":
            if not tracking.task_status_cleared_since_dispatch:
                reasons.append("task_status_completed_ignored_not_cleared_after_dispatch")
            elif not is_meaningful_error(error):
                reasons.append("task_status_completed_ignored_due_vacuum_error")
            else:
                reasons.append(f"task_status_completed_ignored_due_vacuum_error:{error}")
        return wait_for_user_action()

    confirmed = tracking.active_room_confirmed_since_dispatch
    if task == "completed":
        if not tracking.task_status_cleared_since_dispatch:
            reasons.append("task_status_completed_ignored_not_cleared_after_dispatch")
        else:
            # A cloud reconnect can replay the previous task's completion seconds after a
            # fresh dispatch. Give an unconfirmed room one retry interval to show itself.
            if not confirmed and seconds_since_command < DISPATCH_RETRY_INTERVAL_SEC:
                return hold("task_status_completed_unconfirmed_room_waiting")
            if not confirmed and _room_matches(observation, item) is False:
                return fail(
                    f"task_completed_unconfirmed_room:{expected_observed}",
                    "task_status_completed_unconfirmed_room",
                )
            return Decision("complete", tracking, (*reasons, "task_status_completed"))

    if observation.is_post_run_maintenance_state:
        # Only maintenance after a confirmed room belongs to it; leftovers from a
        # previous room must not stick to the newly dispatched one.
        if confirmed:
            return hold(
                "post_run_maintenance_waiting",
                post_run_maintenance_seen=True,
                dispatch_retry_count=0,
            )
        return hold("post_run_maintenance_waiting")

    if vacuum in {"", "unknown", "unavailable"}:
        return hold("vacuum_unavailable_waiting")

    if tracking.post_run_maintenance_seen:
        return hold("post_run_completion_waiting")

    if observation.is_mop_maintenance_state:
        if is_meaningful_error(error):
            return wait_for_user_action()
        return hold("mop_maintenance_waiting")

    if observation.water_tank_block_reason:
        return hold(observation.water_tank_block_reason)

    # Paused drying needs explicit continuation; it is not a resumable paused wash.
    dock_prep_paused = observation.is_dock_prep_paused and not observation.is_drying_state
    if observation.is_dock_prep_state and dock_prep_paused and not task.endswith("_paused"):
        if is_meaningful_error(error):
            return wait_for_user_action()
        if not observation.dock_prep_resume_ready:
            return hold("dock_prep_paused_waiting_resume_ready")
        if seconds_since_command < DISPATCH_RETRY_INTERVAL_SEC:
            return hold("dock_prep_paused_waiting_retry_interval")
        return Decision("resume", tracking, (*reasons, "dock_prep_paused_resume_requested"))

    if vacuum == "paused" or task.endswith("_paused"):
        if is_meaningful_error(error):
            return wait_for_user_action()
        return hold("vacuum_paused_waiting")

    if vacuum in ACTIVE_STATES or observation.is_dock_prep_state:
        room_matches = (
            _room_matches(observation, item)
            if vacuum == "cleaning" and not observation.is_dock_prep_state
            else None
        )
        if room_matches is not False:
            if not room_matches:
                return hold()
            if tracking.dispatch_retry_count > 0:
                reasons.append("dispatch_retry_reset_after_active_confirmation")
            return hold(active_room_confirmed_since_dispatch=True, dispatch_retry_count=0)

        # Redispatching a robot that is already cleaning only resets its target, and the
        # room sensor flips at doorways. Once the room is confirmed, a mismatch is never
        # acted on.
        if confirmed:
            return hold(f"active_room_mismatch_after_confirmation:{expected_observed}")

        progress = observation.cleaning_progress
        if progress is not None and progress < ACTIVE_ROOM_MISMATCH_MIN_PROGRESS:
            return hold(
                f"active_room_mismatch_waiting_progress:{expected_observed}:"
                f"progress_{progress}:min_{ACTIVE_ROOM_MISMATCH_MIN_PROGRESS}"
            )
        if progress is not None and progress >= ACTIVE_ROOM_MISMATCH_MAX_PROGRESS:
            reason = f"active_room_mismatch_unconfirmed_near_completion:{expected_observed}"
            return fail(
                reason,
                f"{reason}:progress_{progress}:max_{ACTIVE_ROOM_MISMATCH_MAX_PROGRESS}",
            )
        if tracking.dispatch_retry_count >= DISPATCH_RETRY_MAX:
            return fail(
                f"active_room_mismatch_retry_exhausted:{expected_observed}",
                "active_room_mismatch_retry_exhausted",
            )
        if seconds_since_command >= DISPATCH_RETRY_INTERVAL_SEC:
            return retry(
                f"active_room_mismatch_retry:{tracking.dispatch_retry_count + 1}:"
                f"{expected_observed}"
            )
        return hold(f"active_room_mismatch_waiting_retry_interval:{expected_observed}")

    if tracking.dispatch_retry_count >= DISPATCH_RETRY_MAX:
        return fail(
            f"dispatch_retry_exhausted:{expected_observed}:vacuum_{vacuum}",
            "dispatch_retry_exhausted",
        )
    if seconds_since_command >= DISPATCH_RETRY_INTERVAL_SEC:
        return retry(f"retry_dispatch_requested:{tracking.dispatch_retry_count + 1}")
    return hold()


def _room_matches(observation: Observation, item: QueueItem) -> bool | None:
    """Return whether the observed room is the queued room, or None when unknown."""
    expected_name = _normalize(item.room_name)
    observed_name = _normalize(observation.observed_room_name)
    if expected_name and observed_name:
        return expected_name == observed_name
    if observation.observed_room_id is not None:
        return item.room_id == observation.observed_room_id
    return None


def _normalize(value: str | None) -> str:
    return (value or "").strip().lower()

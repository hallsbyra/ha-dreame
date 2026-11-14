"""Evaluate runtime robot observations for HA Dreame reconciliation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .queue_core import (
    QueueItem,
    QueueState,
    ReconcileDecision,
    current_item,
    evaluate_reconcile_tick,
)
from .runtime_state import QueueRunTracking


@dataclass(frozen=True, slots=True)
class RuntimeReconcileObservation:
    """One public-safe robot observation for reconcile evaluation."""

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
class RuntimeReconcileEvaluation:
    """Inspectable runtime reconcile evaluation output."""

    decision: ReconcileDecision
    awaiting_completion_event: bool
    expected_room_id: int | None = None
    expected_room_name: str | None = None
    observed_room_id: int | None = None
    observed_room_name: str | None = None
    seconds_since_last_command: float | None = None


def evaluate_runtime_reconcile_observation(
    queue_state: QueueState,
    run_tracking: QueueRunTracking | None,
    observation: RuntimeReconcileObservation,
    *,
    now: datetime,
) -> RuntimeReconcileEvaluation:
    """Evaluate one runtime observation without reading HA state or sending commands."""
    queue_item = current_item(queue_state)
    awaiting_completion_event = _is_awaiting_completion_event(
        queue_state,
        run_tracking,
        queue_item,
    )
    expected_room_id = queue_item.room_id if queue_item is not None else None
    expected_room_name = queue_item.room_name if queue_item is not None else None
    seconds_since_last_command = (
        _seconds_since_last_command(run_tracking.last_command_at, now)
        if awaiting_completion_event and run_tracking is not None
        else None
    )

    decision = evaluate_reconcile_tick(
        vacuum_state=(
            "paused"
            if observation.robot_paused and observation.vacuum_state != "error"
            else observation.vacuum_state
        ),
        task_status=observation.task_status,
        vacuum_error_code=observation.vacuum_error_code,
        awaiting_completion_event=awaiting_completion_event,
        seconds_since_last_command=seconds_since_last_command,
        task_status_cleared_since_dispatch=(
            run_tracking.task_status_cleared_since_dispatch
            if awaiting_completion_event and run_tracking is not None
            else False
        ),
        dispatch_retry_count=(
            run_tracking.dispatch_retry_count
            if awaiting_completion_event and run_tracking is not None
            else 0
        ),
        expected_room_id=expected_room_id,
        observed_room_id=observation.observed_room_id,
        is_dock_prep_state=observation.is_dock_prep_state,
        is_dock_prep_paused=(observation.is_dock_prep_paused and not observation.is_drying_state),
        expected_room_name=expected_room_name,
        observed_room_name=observation.observed_room_name,
        cleaning_progress=observation.cleaning_progress,
        dock_prep_resume_ready=observation.dock_prep_resume_ready,
        water_tank_block_reason=observation.water_tank_block_reason,
        is_mop_maintenance_state=observation.is_mop_maintenance_state,
        is_post_run_maintenance_state=observation.is_post_run_maintenance_state,
        post_run_maintenance_seen=(
            run_tracking.post_run_maintenance_seen
            if awaiting_completion_event and run_tracking is not None
            else False
        ),
        active_room_confirmed_since_dispatch=(
            run_tracking.active_room_confirmed_since_dispatch
            if awaiting_completion_event and run_tracking is not None
            else False
        ),
    )

    return RuntimeReconcileEvaluation(
        decision=decision,
        awaiting_completion_event=awaiting_completion_event,
        expected_room_id=expected_room_id,
        expected_room_name=expected_room_name,
        observed_room_id=observation.observed_room_id,
        observed_room_name=observation.observed_room_name,
        seconds_since_last_command=seconds_since_last_command,
    )


def _is_awaiting_completion_event(
    queue_state: QueueState,
    run_tracking: QueueRunTracking | None,
    queue_item: QueueItem | None,
) -> bool:
    if queue_state.run_state != "running":
        return False
    if run_tracking is None or queue_item is None:
        return False
    if queue_item.status != "running":
        return False
    return (
        queue_state.run_id == run_tracking.run_id
        and queue_state.current_item_id == run_tracking.current_item_id
    )


def _seconds_since_last_command(command_at: str, now: datetime) -> float | None:
    parsed_command_at = _parse_aware_datetime(command_at)
    if parsed_command_at is None or now.tzinfo is None or now.utcoffset() is None:
        return None

    return max(0.0, (now - parsed_command_at).total_seconds())


def _parse_aware_datetime(value: str) -> datetime | None:
    timestamp = str(value or "").strip()
    if not timestamp:
        return None
    if timestamp.endswith("Z"):
        timestamp = f"{timestamp[:-1]}+00:00"

    try:
        parsed = datetime.fromisoformat(timestamp)
    except ValueError:
        return None

    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return None
    return parsed

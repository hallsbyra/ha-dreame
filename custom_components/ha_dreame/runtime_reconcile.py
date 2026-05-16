"""Apply pure reconcile decisions to HA Dreame runtime state."""

from __future__ import annotations

from dataclasses import dataclass, replace

from .queue_core import (
    InvalidOperation,
    QueueState,
    ReconcileDecision,
    complete_current_room,
    external_takeover,
)
from .runtime_state import QueueRunTracking

COMMAND_INTENT_DISPATCH_CURRENT_ROOM = "dispatch_current_room"
COMMAND_INTENT_RESUME_CURRENT_ROOM = "resume_current_room"


@dataclass(frozen=True, slots=True)
class RuntimeReconcileResult:
    """One applied runtime reconcile result."""

    queue_state: QueueState
    run_tracking: QueueRunTracking | None
    command_intent: str | None = None
    command_item_id: str | None = None
    event_reasons: tuple[str, ...] = ()


def apply_reconcile_decision(
    queue_state: QueueState,
    run_tracking: QueueRunTracking | None,
    decision: ReconcileDecision,
) -> RuntimeReconcileResult:
    """Apply one reconcile decision without executing Home Assistant service calls."""
    if not _decision_has_runtime_effect(decision):
        return RuntimeReconcileResult(
            queue_state=queue_state,
            run_tracking=run_tracking,
            event_reasons=decision.event_reasons,
        )

    _validate_tracking_matches_queue(queue_state, run_tracking)
    assert run_tracking is not None

    if decision.mark_out_of_sync_reason is not None:
        return RuntimeReconcileResult(
            queue_state=external_takeover(
                queue_state,
                reason=decision.mark_out_of_sync_reason,
            ),
            run_tracking=None,
            event_reasons=decision.event_reasons,
        )

    if decision.complete_current_room:
        next_state = complete_current_room(queue_state)
        if next_state.current_item_id is None:
            return RuntimeReconcileResult(
                queue_state=next_state,
                run_tracking=None,
                event_reasons=decision.event_reasons,
            )
        return RuntimeReconcileResult(
            queue_state=next_state,
            run_tracking=None,
            command_intent=COMMAND_INTENT_DISPATCH_CURRENT_ROOM,
            command_item_id=next_state.current_item_id,
            event_reasons=decision.event_reasons,
        )

    next_tracking = _apply_tracking_updates(run_tracking, decision)

    if decision.retry_current_room:
        return RuntimeReconcileResult(
            queue_state=queue_state,
            run_tracking=replace(
                next_tracking,
                dispatch_retry_count=next_tracking.dispatch_retry_count + 1,
            ),
            command_intent=COMMAND_INTENT_DISPATCH_CURRENT_ROOM,
            command_item_id=queue_state.current_item_id,
            event_reasons=decision.event_reasons,
        )

    if decision.resume_current_room:
        return RuntimeReconcileResult(
            queue_state=queue_state,
            run_tracking=next_tracking,
            command_intent=COMMAND_INTENT_RESUME_CURRENT_ROOM,
            command_item_id=queue_state.current_item_id,
            event_reasons=decision.event_reasons,
        )

    return RuntimeReconcileResult(
        queue_state=queue_state,
        run_tracking=next_tracking,
        event_reasons=decision.event_reasons,
    )


def _decision_has_runtime_effect(decision: ReconcileDecision) -> bool:
    return (
        decision.complete_current_room
        or decision.retry_current_room
        or decision.resume_current_room
        or decision.mark_out_of_sync_reason is not None
        or decision.set_task_status_cleared_since_dispatch
        or decision.reset_dispatch_retry_count
    )


def _validate_tracking_matches_queue(
    queue_state: QueueState,
    run_tracking: QueueRunTracking | None,
) -> None:
    if run_tracking is None:
        raise InvalidOperation("Runtime reconcile requires run tracking")
    if (
        queue_state.run_id != run_tracking.run_id
        or queue_state.current_item_id != run_tracking.current_item_id
    ):
        raise InvalidOperation("Runtime reconcile tracking does not match current queue run")


def _apply_tracking_updates(
    run_tracking: QueueRunTracking,
    decision: ReconcileDecision,
) -> QueueRunTracking:
    next_tracking = run_tracking
    if decision.set_task_status_cleared_since_dispatch:
        next_tracking = replace(next_tracking, task_status_cleared_since_dispatch=True)
    if decision.reset_dispatch_retry_count:
        next_tracking = replace(next_tracking, dispatch_retry_count=0)
    return next_tracking

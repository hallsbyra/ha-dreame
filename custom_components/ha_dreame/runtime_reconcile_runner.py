"""Shared runtime reconcile evaluation and application helpers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .queue_core import QueueError
from .runtime import HaDreameRuntimeData
from .runtime_observation import build_runtime_reconcile_observation
from .runtime_reconcile import RuntimeReconcileResult, apply_reconcile_decision
from .runtime_reconcile_executor import async_apply_runtime_reconcile_result
from .runtime_reconcile_observation import (
    RuntimeReconcileEvaluation,
    RuntimeReconcileObservation,
    evaluate_runtime_reconcile_observation,
)


@dataclass(frozen=True, slots=True)
class RuntimeReconcileApplyOutcome:
    """Inspectable result from one runtime reconcile apply pass."""

    applied_result: RuntimeReconcileResult
    evaluation: RuntimeReconcileEvaluation
    observation: RuntimeReconcileObservation


def evaluate_runtime_reconcile(
    hass: HomeAssistant,
    runtime_data: HaDreameRuntimeData,
) -> tuple[RuntimeReconcileObservation, RuntimeReconcileEvaluation]:
    """Build and evaluate one runtime reconcile observation."""
    observation = build_runtime_reconcile_observation(
        hass,
        vacuum_entity_id=runtime_data.vacuum_entity_id,
        entity_ids=runtime_data.observation_entity_ids,
    )
    evaluation = evaluate_runtime_reconcile_observation(
        runtime_data.queue_state,
        runtime_data.run_tracking,
        observation,
        now=datetime.now(UTC),
    )

    return observation, evaluation


async def async_evaluate_and_apply_runtime_reconcile(
    hass: HomeAssistant,
    runtime_data: HaDreameRuntimeData,
) -> RuntimeReconcileApplyOutcome:
    """Evaluate and apply one runtime reconcile pass."""
    observation, evaluation = evaluate_runtime_reconcile(hass, runtime_data)
    try:
        result = apply_reconcile_decision(
            runtime_data.queue_state,
            runtime_data.run_tracking,
            evaluation.decision,
        )
    except QueueError as err:
        raise HomeAssistantError(str(err)) from err

    applied_result = await async_apply_runtime_reconcile_result(
        hass,
        runtime_data,
        result,
    )
    return RuntimeReconcileApplyOutcome(
        applied_result=applied_result,
        evaluation=evaluation,
        observation=observation,
    )

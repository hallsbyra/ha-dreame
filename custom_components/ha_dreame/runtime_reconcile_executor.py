"""Home Assistant boundary for applying runtime reconcile results."""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime

from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant

from .audit import async_call_robot_service
from .const import VACUUM_DOMAIN
from .dispatch_executor import async_dispatch_current_room
from .runtime import HaDreameRuntimeData
from .runtime_reconcile import (
    COMMAND_INTENT_DISPATCH_CURRENT_ROOM,
    COMMAND_INTENT_RESUME_CURRENT_ROOM,
    RuntimeReconcileResult,
)


async def async_apply_runtime_reconcile_result(
    hass: HomeAssistant,
    runtime_data: HaDreameRuntimeData,
    result: RuntimeReconcileResult,
) -> RuntimeReconcileResult:
    """Apply one reconcile result to runtime data and execute explicit intents."""
    if result.command_intent == COMMAND_INTENT_DISPATCH_CURRENT_ROOM:
        retry_count = result.run_tracking.dispatch_retry_count if result.run_tracking else 0
        await async_dispatch_current_room(hass, runtime_data, result.queue_state, retry_count)
        return replace(result, run_tracking=runtime_data.run_tracking)

    if result.command_intent == COMMAND_INTENT_RESUME_CURRENT_ROOM:
        # Resume intents are only produced for the tracked current room.
        assert result.run_tracking is not None
        await async_call_robot_service(
            hass,
            runtime_data,
            VACUUM_DOMAIN,
            "start",
            {ATTR_ENTITY_ID: runtime_data.vacuum_entity_id},
        )
        result = replace(
            result,
            run_tracking=replace(result.run_tracking, last_command_at=datetime.now(UTC)),
        )

    runtime_data.set_queue_state(result.queue_state)
    runtime_data.set_run_tracking(result.run_tracking)
    return result

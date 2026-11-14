"""Command-gated execution for planned Dreame dispatch calls."""

from __future__ import annotations

from homeassistant.core import HomeAssistant

from .audit import async_call_robot_service
from .dispatch_plan import DispatchServiceCall, cleaning_mode_entity_id
from .runtime import HaDreameRuntimeData


def observed_cleaning_mode(hass: HomeAssistant, vacuum_entity_id: str) -> str | None:
    """Return the robot's current cleaning-mode select state, if observed."""
    state = hass.states.get(cleaning_mode_entity_id(vacuum_entity_id))
    return state.state if state is not None else None


async def async_execute_dispatch_plan(
    hass: HomeAssistant,
    runtime_data: HaDreameRuntimeData,
    plan: tuple[DispatchServiceCall, ...],
) -> None:
    """Execute planned dispatch service calls in order through the command gate."""
    for planned_call in plan:
        await async_call_robot_service(
            hass,
            runtime_data,
            planned_call.domain,
            planned_call.service,
            dict(planned_call.data),
        )

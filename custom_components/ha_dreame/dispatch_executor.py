"""Command-gated execution for planned Dreame dispatch calls."""

from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .dispatch_plan import DispatchServiceCall, RoomDispatchPlan
from .audit import async_call_robot_service


async def async_execute_dispatch_plan(
    hass: HomeAssistant,
    plan: RoomDispatchPlan,
    *,
    commands_enabled: bool,
) -> tuple[DispatchServiceCall, ...]:
    """Execute planned dispatch service calls when robot commands are enabled."""
    if not commands_enabled:
        raise HomeAssistantError("HA Dreame robot commands are disabled")

    executed: list[DispatchServiceCall] = []
    for planned_call in plan.service_calls:
        await async_call_robot_service(
            hass,
            planned_call.domain,
            planned_call.service,
            dict(planned_call.data),
            blocking=True,
        )
        executed.append(planned_call)

    return tuple(executed)

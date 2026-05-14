"""Tests for command-gated Dreame dispatch execution."""

import pytest

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError

from custom_components.ha_dreame.const import DREAME_VACUUM_DOMAIN
from custom_components.ha_dreame.dispatch_executor import (
    async_execute_dispatch_plan,
)
from custom_components.ha_dreame.dispatch_plan import (
    DispatchServiceCall,
    RoomDispatchPlan,
)


def _plan() -> RoomDispatchPlan:
    return RoomDispatchPlan(
        item_id="item-1",
        room_id=7,
        room_name="Room 7",
        effective_overrides={"repeats": 2},
        service_calls=(
            DispatchServiceCall(
                domain=DREAME_VACUUM_DOMAIN,
                service="vacuum_set_custom_cleaning",
                data={
                    "entity_id": "vacuum.robot",
                    "repeats": [2],
                    "segment_id": [7],
                },
            ),
            DispatchServiceCall(
                domain=DREAME_VACUUM_DOMAIN,
                service="vacuum_clean_segment",
                data={
                    "entity_id": "vacuum.robot",
                    "repeats": 2,
                    "segments": [7],
                },
            ),
        ),
    )


async def test_execute_dispatch_plan_rejects_disabled_command_gate(
    hass: HomeAssistant,
) -> None:
    """Test disabled command gate prevents all planned service calls."""
    calls: list[ServiceCall] = []

    async def _record_call(call: ServiceCall) -> None:
        calls.append(call)

    hass.services.async_register(
        DREAME_VACUUM_DOMAIN,
        "vacuum_clean_segment",
        _record_call,
    )

    with pytest.raises(HomeAssistantError, match="robot commands are disabled"):
        await async_execute_dispatch_plan(
            hass,
            _plan(),
            commands_enabled=False,
        )

    assert calls == []


async def test_execute_dispatch_plan_calls_services_in_order(
    hass: HomeAssistant,
) -> None:
    """Test enabled command gate executes planned service calls in order."""
    calls: list[tuple[str, str, dict[str, object]]] = []

    async def _record_call(call: ServiceCall) -> None:
        calls.append((call.domain, call.service, dict(call.data)))

    hass.services.async_register(
        DREAME_VACUUM_DOMAIN,
        "vacuum_set_custom_cleaning",
        _record_call,
    )
    hass.services.async_register(
        DREAME_VACUUM_DOMAIN,
        "vacuum_clean_segment",
        _record_call,
    )
    plan = _plan()

    executed = await async_execute_dispatch_plan(
        hass,
        plan,
        commands_enabled=True,
    )

    assert executed == plan.service_calls
    assert calls == [
        (
            DREAME_VACUUM_DOMAIN,
            "vacuum_set_custom_cleaning",
            {
                "entity_id": "vacuum.robot",
                "repeats": [2],
                "segment_id": [7],
            },
        ),
        (
            DREAME_VACUUM_DOMAIN,
            "vacuum_clean_segment",
            {
                "entity_id": "vacuum.robot",
                "repeats": 2,
                "segments": [7],
            },
        ),
    ]


async def test_execute_dispatch_plan_stops_after_service_failure(
    hass: HomeAssistant,
) -> None:
    """Test service errors stop later planned calls."""
    calls: list[tuple[str, str]] = []

    async def _raise_call(call: ServiceCall) -> None:
        calls.append((call.domain, call.service))
        raise HomeAssistantError("dispatch failed")

    async def _record_call(call: ServiceCall) -> None:
        calls.append((call.domain, call.service))

    hass.services.async_register(
        DREAME_VACUUM_DOMAIN,
        "vacuum_set_custom_cleaning",
        _raise_call,
    )
    hass.services.async_register(
        DREAME_VACUUM_DOMAIN,
        "vacuum_clean_segment",
        _record_call,
    )

    with pytest.raises(HomeAssistantError, match="dispatch failed"):
        await async_execute_dispatch_plan(
            hass,
            _plan(),
            commands_enabled=True,
        )

    assert calls == [(DREAME_VACUUM_DOMAIN, "vacuum_set_custom_cleaning")]

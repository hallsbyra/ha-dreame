"""Tests for HA Dreame integration setup."""

import pytest

from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.ha_dreame.const import (
    CONF_VACUUM_ENTITY_ID,
    DOMAIN,
    DREAME_VACUUM_DOMAIN,
    TITLE,
)
from custom_components.ha_dreame.runtime import HaDreameRuntimeData

pytestmark = pytest.mark.usefixtures("mock_dreame_vacuum_dependency")


def _register_entity(
    hass: HomeAssistant,
    entity_id: str,
    *,
    platform: str = DREAME_VACUUM_DOMAIN,
    unique_id: str = "robot-1",
) -> str:
    """Register an entity and return its entity id."""
    domain, object_id = entity_id.split(".", maxsplit=1)
    registry = er.async_get(hass)
    entry = registry.async_get_or_create(
        domain,
        platform,
        unique_id,
        suggested_object_id=object_id,
    )
    return entry.entity_id


def _mock_entry(data: dict[str, str]) -> MockConfigEntry:
    return MockConfigEntry(domain=DOMAIN, title=TITLE, data=data)


async def test_setup_entry_attaches_runtime_data(hass: HomeAssistant) -> None:
    """Test that a config entry exposes typed runtime data."""
    vacuum_entity_id = _register_entity(hass, "vacuum.dreame_robot")
    entry = _mock_entry({CONF_VACUUM_ENTITY_ID: vacuum_entity_id})
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert isinstance(entry.runtime_data, HaDreameRuntimeData)
    assert entry.runtime_data.vacuum_entity_id == vacuum_entity_id
    assert hass.data[DOMAIN][entry.entry_id] is entry


async def test_unload_entry_clears_runtime_data(hass: HomeAssistant) -> None:
    """Test that unloading clears runtime state."""
    vacuum_entity_id = _register_entity(hass, "vacuum.dreame_robot")
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=TITLE,
        data={CONF_VACUUM_ENTITY_ID: vacuum_entity_id},
    )
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()

    assert not hasattr(entry, "runtime_data")
    assert entry.entry_id not in hass.data[DOMAIN]


@pytest.mark.parametrize(
    ("data", "entity_id", "platform"),
    [
        pytest.param({}, None, DREAME_VACUUM_DOMAIN, id="missing-config-data"),
        pytest.param(
            {CONF_VACUUM_ENTITY_ID: "sensor.dreame_robot"},
            "sensor.dreame_robot",
            DREAME_VACUUM_DOMAIN,
            id="non-vacuum-domain",
        ),
        pytest.param(
            {CONF_VACUUM_ENTITY_ID: "vacuum.other_robot"},
            "vacuum.other_robot",
            "other_vacuum",
            id="non-dreame-platform",
        ),
    ],
)
async def test_setup_entry_rejects_invalid_stored_vacuum(
    hass: HomeAssistant,
    data: dict[str, str],
    entity_id: str | None,
    platform: str,
) -> None:
    """Test invalid stored dependency references fail setup."""
    if entity_id is not None:
        _register_entity(hass, entity_id, platform=platform)
    entry = _mock_entry(data)
    entry.add_to_hass(hass)

    assert not await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert not hasattr(entry, "runtime_data")
    assert entry.entry_id not in hass.data.get(DOMAIN, {})

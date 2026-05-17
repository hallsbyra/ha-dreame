"""Tests for the HA Dreame config flow."""

import pytest

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.ha_dreame.const import (
    CONF_ALLOW_ROBOT_COMMANDS,
    CONF_AUTO_RECONCILE_ENABLED,
    CONF_CLEAN_WATER_TANK_STATUS_ENTITY_ID,
    CONF_CLEANING_PROGRESS_ENTITY_ID,
    CONF_CURRENT_ROOM_ENTITY_ID,
    CONF_ERROR_ENTITY_ID,
    CONF_ROBOT_STATE_ENTITY_ID,
    CONF_SELF_WASH_BASE_STATUS_ENTITY_ID,
    CONF_TASK_STATUS_ENTITY_ID,
    CONF_VACUUM_ENTITY_ID,
    DOMAIN,
    DREAME_VACUUM_DOMAIN,
)

pytestmark = pytest.mark.usefixtures("mock_dreame_vacuum_dependency")


def _schema_keys(schema: object) -> set[str]:
    return {getattr(key, "schema", key) for key in getattr(schema, "schema", {})}


def _register_vacuum(
    hass: HomeAssistant,
    *,
    platform: str = DREAME_VACUUM_DOMAIN,
    unique_id: str = "robot-1",
    suggested_object_id: str = "dreame_robot",
) -> str:
    registry = er.async_get(hass)
    entry = registry.async_get_or_create(
        "vacuum",
        platform,
        unique_id,
        suggested_object_id=suggested_object_id,
    )
    hass.states.async_set(entry.entity_id, "docked", {"friendly_name": "Dreame Robot"})
    return entry.entity_id


def _options_defaults(schema: object) -> dict[str, object]:
    return schema({})


OBSERVATION_ENTITY_OPTIONS = {
    CONF_CLEAN_WATER_TANK_STATUS_ENTITY_ID,
    CONF_CLEANING_PROGRESS_ENTITY_ID,
    CONF_CURRENT_ROOM_ENTITY_ID,
    CONF_ERROR_ENTITY_ID,
    CONF_ROBOT_STATE_ENTITY_ID,
    CONF_SELF_WASH_BASE_STATUS_ENTITY_ID,
    CONF_TASK_STATUS_ENTITY_ID,
}


async def test_user_flow_creates_entry(hass: HomeAssistant) -> None:
    """Test the user flow creates an entry for one Dreame vacuum."""
    vacuum_entity_id = _register_vacuum(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_USER},
    )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] is None
    assert CONF_VACUUM_ENTITY_ID in _schema_keys(result["data_schema"])

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_VACUUM_ENTITY_ID: vacuum_entity_id},
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "Dreame Robot"
    assert result["data"] == {CONF_VACUUM_ENTITY_ID: vacuum_entity_id}


async def test_user_flow_rejects_missing_entity(hass: HomeAssistant) -> None:
    """Test missing vacuum entity ids are rejected."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_USER},
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_VACUUM_ENTITY_ID: "vacuum.missing"},
    )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {CONF_VACUUM_ENTITY_ID: "entity_not_found"}


async def test_user_flow_rejects_non_vacuum_entity(hass: HomeAssistant) -> None:
    """Test non-vacuum entity ids are rejected."""
    hass.states.async_set("sensor.robot", "ready")

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_USER},
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_VACUUM_ENTITY_ID: "sensor.robot"},
    )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {CONF_VACUUM_ENTITY_ID: "not_vacuum"}


async def test_user_flow_rejects_non_dreame_vacuum(hass: HomeAssistant) -> None:
    """Test non-Dreame vacuum entities are rejected when registry platform is known."""
    vacuum_entity_id = _register_vacuum(hass, platform="other_vacuum")

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_USER},
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_VACUUM_ENTITY_ID: vacuum_entity_id},
    )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {CONF_VACUUM_ENTITY_ID: "not_dreame_vacuum"}


async def test_user_flow_aborts_when_selected_vacuum_already_configured(
    hass: HomeAssistant,
) -> None:
    """Test the same Dreame vacuum cannot be configured twice."""
    vacuum_entity_id = _register_vacuum(hass)

    first_result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_USER},
    )
    first_result = await hass.config_entries.flow.async_configure(
        first_result["flow_id"],
        {CONF_VACUUM_ENTITY_ID: vacuum_entity_id},
    )

    assert first_result["type"] is FlowResultType.CREATE_ENTRY

    second_result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_USER},
    )
    second_result = await hass.config_entries.flow.async_configure(
        second_result["flow_id"],
        {CONF_VACUUM_ENTITY_ID: vacuum_entity_id},
    )

    assert second_result["type"] is FlowResultType.ABORT
    assert second_result["reason"] == "already_configured"


async def test_options_flow_defaults_robot_commands_disabled(
    hass: HomeAssistant,
) -> None:
    """Test the options flow exposes command dispatch disabled by default."""
    vacuum_entity_id = _register_vacuum(hass)
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Dreame Robot",
        data={CONF_VACUUM_ENTITY_ID: vacuum_entity_id},
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)

    assert result["type"] is FlowResultType.FORM
    assert CONF_ALLOW_ROBOT_COMMANDS in _schema_keys(result["data_schema"])
    assert CONF_AUTO_RECONCILE_ENABLED in _schema_keys(result["data_schema"])
    assert _options_defaults(result["data_schema"]) == {
        CONF_ALLOW_ROBOT_COMMANDS: False,
        CONF_AUTO_RECONCILE_ENABLED: False,
    }


async def test_options_flow_exposes_observation_entity_options(
    hass: HomeAssistant,
) -> None:
    """Test the options flow exposes explicit observation entity selectors."""
    vacuum_entity_id = _register_vacuum(hass)
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Dreame Robot",
        data={CONF_VACUUM_ENTITY_ID: vacuum_entity_id},
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)

    assert result["type"] is FlowResultType.FORM
    assert OBSERVATION_ENTITY_OPTIONS.issubset(_schema_keys(result["data_schema"]))


async def test_options_flow_can_enable_robot_commands(hass: HomeAssistant) -> None:
    """Test the command gate can be explicitly enabled."""
    vacuum_entity_id = _register_vacuum(hass)
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Dreame Robot",
        data={CONF_VACUUM_ENTITY_ID: vacuum_entity_id},
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {CONF_ALLOW_ROBOT_COMMANDS: True},
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"] == {CONF_ALLOW_ROBOT_COMMANDS: True}


async def test_options_flow_can_enable_auto_reconcile(
    hass: HomeAssistant,
) -> None:
    """Test automatic reconcile can be explicitly enabled."""
    vacuum_entity_id = _register_vacuum(hass)
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Dreame Robot",
        data={CONF_VACUUM_ENTITY_ID: vacuum_entity_id},
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {
            CONF_ALLOW_ROBOT_COMMANDS: True,
            CONF_AUTO_RECONCILE_ENABLED: True,
        },
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"] == {
        CONF_ALLOW_ROBOT_COMMANDS: True,
        CONF_AUTO_RECONCILE_ENABLED: True,
    }


async def test_options_flow_can_disable_robot_commands(hass: HomeAssistant) -> None:
    """Test the command gate can be explicitly disabled again."""
    vacuum_entity_id = _register_vacuum(hass)
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Dreame Robot",
        data={CONF_VACUUM_ENTITY_ID: vacuum_entity_id},
        options={CONF_ALLOW_ROBOT_COMMANDS: True},
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {CONF_ALLOW_ROBOT_COMMANDS: False},
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"] == {CONF_ALLOW_ROBOT_COMMANDS: False}


async def test_options_flow_can_store_observation_entities(
    hass: HomeAssistant,
) -> None:
    """Test configured observation entity ids are stored with command options."""
    vacuum_entity_id = _register_vacuum(hass)
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Dreame Robot",
        data={CONF_VACUUM_ENTITY_ID: vacuum_entity_id},
    )
    entry.add_to_hass(hass)
    observation_options = {
        CONF_CLEAN_WATER_TANK_STATUS_ENTITY_ID: "sensor.robot_clean_water_tank",
        CONF_CLEANING_PROGRESS_ENTITY_ID: "sensor.robot_cleaning_progress",
        CONF_CURRENT_ROOM_ENTITY_ID: "sensor.robot_current_room",
        CONF_ERROR_ENTITY_ID: "sensor.robot_error",
        CONF_ROBOT_STATE_ENTITY_ID: "sensor.robot_state",
        CONF_SELF_WASH_BASE_STATUS_ENTITY_ID: "sensor.robot_self_wash_base",
        CONF_TASK_STATUS_ENTITY_ID: "sensor.robot_task_status",
    }
    for entity_id in observation_options.values():
        hass.states.async_set(entity_id, "ready")

    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {CONF_ALLOW_ROBOT_COMMANDS: True, **observation_options},
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"] == {CONF_ALLOW_ROBOT_COMMANDS: True, **observation_options}


async def test_options_flow_rejects_missing_observation_entity(
    hass: HomeAssistant,
) -> None:
    """Test explicit observation entity ids must exist."""
    vacuum_entity_id = _register_vacuum(hass)
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Dreame Robot",
        data={CONF_VACUUM_ENTITY_ID: vacuum_entity_id},
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {
            CONF_ALLOW_ROBOT_COMMANDS: False,
            CONF_TASK_STATUS_ENTITY_ID: "sensor.missing_task_status",
        },
    )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {CONF_TASK_STATUS_ENTITY_ID: "entity_not_found"}

"""Tests for extracting runtime observations from Home Assistant state."""

from homeassistant.core import HomeAssistant

from custom_components.ha_dreame.runtime_observation import (
    RuntimeObservationEntityIds,
    build_runtime_reconcile_observation,
)


def test_observation_reads_vacuum_state_without_companion_sensors(
    hass: HomeAssistant,
) -> None:
    """Test the vacuum entity itself is enough for a safe partial observation."""
    hass.states.async_set("vacuum.dreame_robot", "cleaning")

    observation = build_runtime_reconcile_observation(
        hass,
        vacuum_entity_id="vacuum.dreame_robot",
    )

    assert observation.vacuum_state == "cleaning"
    assert observation.task_status == ""
    assert observation.vacuum_error_code == ""
    assert observation.observed_room_id is None
    assert observation.observed_room_name is None
    assert observation.cleaning_progress is None
    assert observation.is_dock_prep_state is False
    assert observation.is_mop_maintenance_state is False


def test_observation_reads_conventional_companion_sensors(
    hass: HomeAssistant,
) -> None:
    """Test convention-derived Dreame companion sensors populate observations."""
    hass.states.async_set("vacuum.dreame_robot", "cleaning")
    hass.states.async_set("sensor.dreame_robot_task_status", "room_cleaning")
    hass.states.async_set(
        "sensor.dreame_robot_current_room",
        "Kitchen",
        {"room_id": "7", "room_name": "Kitchen"},
    )
    hass.states.async_set("sensor.dreame_robot_error", "no_error")
    hass.states.async_set("sensor.dreame_robot_cleaning_progress", "42")

    observation = build_runtime_reconcile_observation(
        hass,
        vacuum_entity_id="vacuum.dreame_robot",
    )

    assert observation.vacuum_state == "cleaning"
    assert observation.task_status == "room_cleaning"
    assert observation.vacuum_error_code == "no_error"
    assert observation.observed_room_id == 7
    assert observation.observed_room_name == "Kitchen"
    assert observation.cleaning_progress == 42


def test_observation_explicit_entity_ids_override_conventional_sensors(
    hass: HomeAssistant,
) -> None:
    """Test callers can provide explicit companion entity ids."""
    hass.states.async_set("vacuum.dreame_robot", "cleaning")
    hass.states.async_set("sensor.dreame_robot_task_status", "wrong_conventional")
    hass.states.async_set("sensor.robot_task", "room_cleaning")
    hass.states.async_set("sensor.robot_room", "12")

    observation = build_runtime_reconcile_observation(
        hass,
        vacuum_entity_id="vacuum.dreame_robot",
        entity_ids=RuntimeObservationEntityIds(
            task_status_entity_id="sensor.robot_task",
            current_room_entity_id="sensor.robot_room",
        ),
    )

    assert observation.task_status == "room_cleaning"
    assert observation.observed_room_id == 12
    assert observation.observed_room_name is None


def test_observation_ignores_missing_unknown_and_unavailable_values(
    hass: HomeAssistant,
) -> None:
    """Test unavailable companion data stays absent instead of becoming signal."""
    hass.states.async_set("vacuum.dreame_robot", "unknown")
    hass.states.async_set("sensor.dreame_robot_task_status", "unavailable")
    hass.states.async_set("sensor.dreame_robot_current_room", "unknown")
    hass.states.async_set("sensor.dreame_robot_error", "none")
    hass.states.async_set("sensor.dreame_robot_cleaning_progress", "bad-value")

    observation = build_runtime_reconcile_observation(
        hass,
        vacuum_entity_id="vacuum.dreame_robot",
    )

    assert observation.vacuum_state == ""
    assert observation.task_status == ""
    assert observation.vacuum_error_code == ""
    assert observation.observed_room_id is None
    assert observation.observed_room_name is None
    assert observation.cleaning_progress is None


def test_observation_extracts_current_room_from_state_variants(
    hass: HomeAssistant,
) -> None:
    """Test current-room state supports numeric ids and textual names."""
    hass.states.async_set("vacuum.dreame_robot", "cleaning")
    hass.states.async_set("sensor.dreame_robot_current_room", "15")

    observation = build_runtime_reconcile_observation(
        hass,
        vacuum_entity_id="vacuum.dreame_robot",
    )

    assert observation.observed_room_id == 15
    assert observation.observed_room_name is None

    hass.states.async_set("sensor.dreame_robot_current_room", "Hall")

    observation = build_runtime_reconcile_observation(
        hass,
        vacuum_entity_id="vacuum.dreame_robot",
    )

    assert observation.observed_room_id is None
    assert observation.observed_room_name == "Hall"


def test_observation_detects_mop_remove_install_maintenance(
    hass: HomeAssistant,
) -> None:
    """Test mop maintenance detail states become explicit observation flags."""
    hass.states.async_set("vacuum.dreame_robot", "docked")
    hass.states.async_set("sensor.dreame_robot_state", "returning_remove_mop")
    hass.states.async_set("sensor.dreame_robot_task_status", "room_cleaning")
    hass.states.async_set("sensor.dreame_robot_current_room", "7")

    observation = build_runtime_reconcile_observation(
        hass,
        vacuum_entity_id="vacuum.dreame_robot",
    )

    assert observation.is_returning_state is True
    assert observation.is_mop_maintenance_state is True
    assert observation.observed_room_id == 7


def test_observation_detects_paused_dock_prep_while_vacuum_reports_cleaning(
    hass: HomeAssistant,
) -> None:
    """Test dock-prep pause is visible even if high-level vacuum state is cleaning."""
    hass.states.async_set("vacuum.dreame_robot", "cleaning")
    hass.states.async_set("sensor.dreame_robot_state", "washing_paused")
    hass.states.async_set("sensor.dreame_robot_self_wash_base_status", "paused")
    hass.states.async_set("sensor.dreame_robot_clean_water_tank_status", "installed")

    observation = build_runtime_reconcile_observation(
        hass,
        vacuum_entity_id="vacuum.dreame_robot",
    )

    assert observation.vacuum_state == "cleaning"
    assert observation.is_dock_prep_state is True
    assert observation.is_dock_prep_paused is True
    assert observation.dock_prep_resume_ready is True

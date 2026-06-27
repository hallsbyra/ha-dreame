"""Read runtime reconcile observations from Home Assistant state."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.core import HomeAssistant, State

from .queue_core import MOP_MAINTENANCE_TASK_STATUSES
from .runtime_reconcile_observation import RuntimeReconcileObservation


ABSENT_STATES = {"", "unknown", "unavailable", "none", "null"}
DOCK_PREP_STATE_FRAGMENTS = ("wash", "washing", "dry", "drying", "dock_prep")
MOP_MAINTENANCE_STATE_FRAGMENTS = (
    "remove_mop",
    "install_mop",
    "mop_remove",
    "mop_install",
)
READY_WATER_TANK_STATES = {"installed", "normal", "ok", "ready", "available"}


@dataclass(frozen=True, slots=True)
class RuntimeObservationEntityIds:
    """Optional explicit entity ids for companion Dreame observation sensors."""

    task_status_entity_id: str | None = None
    robot_state_entity_id: str | None = None
    current_room_entity_id: str | None = None
    error_entity_id: str | None = None
    cleaning_progress_entity_id: str | None = None
    self_wash_base_status_entity_id: str | None = None
    clean_water_tank_status_entity_id: str | None = None


def build_runtime_reconcile_observation(
    hass: HomeAssistant,
    *,
    vacuum_entity_id: str,
    entity_ids: RuntimeObservationEntityIds | None = None,
) -> RuntimeReconcileObservation:
    """Build a read-only reconcile observation from Home Assistant state."""
    resolved_entity_ids = entity_ids or RuntimeObservationEntityIds()
    vacuum_state = _state_value(hass.states.get(vacuum_entity_id))
    task_status = _state_value(
        _get_companion_state(
            hass,
            vacuum_entity_id,
            explicit_entity_id=resolved_entity_ids.task_status_entity_id,
            suffix="task_status",
        )
    )
    robot_state = _state_value(
        _get_companion_state(
            hass,
            vacuum_entity_id,
            explicit_entity_id=resolved_entity_ids.robot_state_entity_id,
            suffix="state",
        )
    )
    current_room_state = _get_companion_state(
        hass,
        vacuum_entity_id,
        explicit_entity_id=resolved_entity_ids.current_room_entity_id,
        suffix="current_room",
    )
    error_code = _state_value(
        _get_companion_state(
            hass,
            vacuum_entity_id,
            explicit_entity_id=resolved_entity_ids.error_entity_id,
            suffix="error",
        )
    )
    cleaning_progress = _int_state_value(
        _get_companion_state(
            hass,
            vacuum_entity_id,
            explicit_entity_id=resolved_entity_ids.cleaning_progress_entity_id,
            suffix="cleaning_progress",
        )
    )
    self_wash_base_status = _state_value(
        _get_companion_state(
            hass,
            vacuum_entity_id,
            explicit_entity_id=resolved_entity_ids.self_wash_base_status_entity_id,
            suffix="self_wash_base_status",
        )
    )
    clean_water_tank_status = _state_value(
        _get_companion_state(
            hass,
            vacuum_entity_id,
            explicit_entity_id=resolved_entity_ids.clean_water_tank_status_entity_id,
            suffix="clean_water_tank_status",
        )
    )
    observed_room_id, observed_room_name = _current_room(current_room_state)

    return RuntimeReconcileObservation(
        vacuum_state=vacuum_state,
        task_status=task_status,
        vacuum_error_code=error_code,
        observed_room_id=observed_room_id,
        observed_room_name=observed_room_name,
        cleaning_progress=cleaning_progress,
        is_dock_prep_state=_is_dock_prep_state(robot_state, self_wash_base_status),
        is_dock_prep_paused=_is_dock_prep_paused(robot_state, self_wash_base_status),
        dock_prep_resume_ready=_is_dock_prep_resume_ready(clean_water_tank_status),
        is_mop_maintenance_state=_is_mop_maintenance_state(task_status, robot_state),
        is_returning_state=_is_returning_state(vacuum_state, robot_state),
    )


def _get_companion_state(
    hass: HomeAssistant,
    vacuum_entity_id: str,
    *,
    explicit_entity_id: str | None,
    suffix: str,
) -> State | None:
    if explicit_entity_id:
        return hass.states.get(explicit_entity_id)

    return hass.states.get(_conventional_sensor_entity_id(vacuum_entity_id, suffix))


def _conventional_sensor_entity_id(vacuum_entity_id: str, suffix: str) -> str:
    object_id = vacuum_entity_id.split(".", maxsplit=1)[-1]
    return f"sensor.{object_id}_{suffix}"


def _state_value(state: State | None) -> str:
    if state is None:
        return ""

    value = _normalize_absent(state.state)
    return value or ""


def _normalize_absent(value: Any) -> str | None:
    normalized = str(value or "").strip()
    if normalized.lower() in ABSENT_STATES:
        return None
    return normalized


def _int_state_value(state: State | None) -> int | None:
    value = _state_value(state)
    if not value:
        return None

    try:
        return int(float(value))
    except ValueError:
        return None


def _current_room(state: State | None) -> tuple[int | None, str | None]:
    if state is None:
        return None, None

    room_id = _first_int_attribute(state, "room_id", "id")
    room_name = _first_string_attribute(state, "room_name", "name")
    state_value = _state_value(state)

    if room_id is None:
        room_id = _parse_int(state_value)
    if room_name is None and state_value and _parse_int(state_value) is None:
        room_name = state_value or None

    return room_id, room_name


def _first_int_attribute(state: State, *keys: str) -> int | None:
    for key in keys:
        value = state.attributes.get(key)
        parsed = _parse_int(value)
        if parsed is not None:
            return parsed
    return None


def _first_string_attribute(state: State, *keys: str) -> str | None:
    for key in keys:
        value = _normalize_absent(state.attributes.get(key))
        if value:
            return value
    return None


def _parse_int(value: Any) -> int | None:
    if value is None:
        return None

    try:
        return int(float(str(value).strip()))
    except ValueError:
        return None


def _is_returning_state(vacuum_state: str, robot_state: str) -> bool:
    normalized_states = {_normalize_signal(vacuum_state), _normalize_signal(robot_state)}
    return any("returning" in state or state.startswith("return_") for state in normalized_states)


def _is_mop_maintenance_state(task_status: str, robot_state: str) -> bool:
    normalized_task = _normalize_signal(task_status)
    normalized_robot_state = _normalize_signal(robot_state)
    if normalized_task in MOP_MAINTENANCE_TASK_STATUSES:
        return True
    return any(fragment in normalized_robot_state for fragment in MOP_MAINTENANCE_STATE_FRAGMENTS)


def _is_dock_prep_state(robot_state: str, self_wash_base_status: str) -> bool:
    combined_state = f"{_normalize_signal(robot_state)} {_normalize_signal(self_wash_base_status)}"
    return any(fragment in combined_state for fragment in DOCK_PREP_STATE_FRAGMENTS)


def _is_dock_prep_paused(robot_state: str, self_wash_base_status: str) -> bool:
    combined_state = f"{_normalize_signal(robot_state)} {_normalize_signal(self_wash_base_status)}"
    return "paused" in combined_state or "pause" in combined_state


def _is_dock_prep_resume_ready(clean_water_tank_status: str) -> bool:
    normalized_status = _normalize_signal(clean_water_tank_status)
    return normalized_status in READY_WATER_TANK_STATES


def _normalize_signal(value: str) -> str:
    return str(value or "").strip().lower()

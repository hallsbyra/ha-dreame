"""Read runtime reconcile observations from Home Assistant state."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from homeassistant.core import HomeAssistant, State

from .const import (
    CONF_CLEAN_WATER_TANK_STATUS_ENTITY_ID,
    CONF_CLEANING_PROGRESS_ENTITY_ID,
    CONF_CURRENT_ROOM_ENTITY_ID,
    CONF_ERROR_ENTITY_ID,
    CONF_ROBOT_STATE_ENTITY_ID,
    CONF_SELF_WASH_BASE_STATUS_ENTITY_ID,
    CONF_TASK_STATUS_ENTITY_ID,
    companion_entity_id,
    optional_entity_id,
)
from .reconcile_core import Observation


ABSENT_STATES = {"", "unknown", "unavailable", "none", "null"}
DOCK_PREP_STATE_FRAGMENTS = ("wash", "washing", "dry", "drying", "dock_prep")
POST_RUN_MAINTENANCE_STATE_FRAGMENTS = ("auto_empty",)
MOP_MAINTENANCE_TASK_STATUSES = {
    "returning_to_remove_mop",
    "returning_to_install_mop",
}
MOP_MAINTENANCE_STATE_FRAGMENTS = (
    "remove_mop",
    "install_mop",
    "mop_remove",
    "mop_install",
)
READY_WATER_TANK_STATES = {"installed", "normal", "ok", "ready", "available"}
# Option key -> dreame_vacuum companion sensor suffix used when the option is unset.
OBSERVATION_SENSOR_SUFFIXES = {
    CONF_TASK_STATUS_ENTITY_ID: "task_status",
    CONF_ROBOT_STATE_ENTITY_ID: "state",
    CONF_CURRENT_ROOM_ENTITY_ID: "current_room",
    CONF_ERROR_ENTITY_ID: "error",
    CONF_CLEANING_PROGRESS_ENTITY_ID: "cleaning_progress",
    CONF_SELF_WASH_BASE_STATUS_ENTITY_ID: "self_wash_base_status",
    CONF_CLEAN_WATER_TANK_STATUS_ENTITY_ID: "clean_water_tank_status",
}


@dataclass(frozen=True, slots=True)
class RuntimeObservationEntityIds:
    """Companion observation sensors: explicit options win over Dreame naming."""

    task_status_entity_id: str
    robot_state_entity_id: str
    current_room_entity_id: str
    error_entity_id: str
    cleaning_progress_entity_id: str
    self_wash_base_status_entity_id: str
    clean_water_tank_status_entity_id: str

    @classmethod
    def for_vacuum(
        cls,
        vacuum_entity_id: str,
        options: Mapping[str, Any] | None = None,
    ) -> RuntimeObservationEntityIds:
        """Resolve each companion sensor from options or the vacuum's naming convention."""
        options = options or {}
        return cls(
            **{
                option: optional_entity_id(options.get(option))
                or companion_entity_id(vacuum_entity_id, "sensor", suffix)
                for option, suffix in OBSERVATION_SENSOR_SUFFIXES.items()
            }
        )


def build_runtime_reconcile_observation(
    hass: HomeAssistant,
    *,
    vacuum_entity_id: str,
    entity_ids: RuntimeObservationEntityIds | None = None,
    task_status_override: str | None = None,
) -> Observation:
    """Build a read-only reconcile observation from Home Assistant state.

    A task status override replaces the sensor state, for a transition captured by an
    event before the state machine is read.
    """
    ids = entity_ids or RuntimeObservationEntityIds.for_vacuum(vacuum_entity_id)
    vacuum = hass.states.get(vacuum_entity_id)
    vacuum_state = _state_value(vacuum)
    task_status = (
        task_status_override
        if task_status_override is not None
        else _state_value(hass.states.get(ids.task_status_entity_id))
    )
    robot_state = _state_value(hass.states.get(ids.robot_state_entity_id))
    current_room_state = hass.states.get(ids.current_room_entity_id)
    error_code = _state_value(hass.states.get(ids.error_entity_id))
    cleaning_progress = _int_state_value(hass.states.get(ids.cleaning_progress_entity_id))
    self_wash_base_status = _state_value(hass.states.get(ids.self_wash_base_status_entity_id))
    clean_tank = hass.states.get(ids.clean_water_tank_status_entity_id)
    clean_water_tank_status = _state_value(clean_tank)
    dirty_tank = hass.states.get(
        companion_entity_id(vacuum_entity_id, "sensor", "dirty_water_tank_status")
    )
    water_tank_block_reason = ""
    # Missing optional sensors remain compatible; present but unknown sensors block recovery.
    if dirty_tank is not None and normalize_signal(_state_value(dirty_tank)) not in (
        READY_WATER_TANK_STATES
    ):
        water_tank_block_reason = "dirty_water_tank_not_ready"
    elif (
        clean_tank is not None
        and normalize_signal(clean_water_tank_status) not in READY_WATER_TANK_STATES
    ):
        water_tank_block_reason = "clean_water_tank_not_ready"
    status = _state_value(
        hass.states.get(companion_entity_id(vacuum_entity_id, "sensor", "status"))
    )
    robot_paused = (
        normalize_signal(status) == "paused"
        or (
            vacuum is not None
            and normalize_signal(str(vacuum.attributes.get("status", ""))) == "paused"
        )
        or _vacuum_attributes_report_paused(vacuum)
    )
    is_drying_state = "drying" in f"{robot_state} {self_wash_base_status}".lower() or (
        vacuum is not None and vacuum.attributes.get("drying") is True
    )
    observed_room_id, observed_room_name = _current_room(current_room_state)

    return Observation(
        vacuum_state=vacuum_state,
        task_status=task_status,
        vacuum_error_code=error_code,
        robot_paused=robot_paused,
        is_drying_state=is_drying_state,
        water_tank_block_reason=water_tank_block_reason,
        observed_room_id=observed_room_id,
        observed_room_name=observed_room_name,
        cleaning_progress=cleaning_progress,
        is_dock_prep_state=_is_dock_prep_state(robot_state, self_wash_base_status),
        is_dock_prep_paused=_is_dock_prep_paused(
            robot_state,
            self_wash_base_status,
            vacuum,
        ),
        dock_prep_resume_ready=(
            _is_dock_prep_resume_ready(clean_water_tank_status) and not water_tank_block_reason
        ),
        is_mop_maintenance_state=_is_mop_maintenance_state(task_status, robot_state),
        is_post_run_maintenance_state=_is_post_run_maintenance_state(
            robot_state,
            self_wash_base_status,
        ),
    )


def normalize_signal(value: object) -> str:
    """Normalize a state value for case-insensitive comparison."""
    return str(value or "").strip().lower()


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


def _is_mop_maintenance_state(task_status: str, robot_state: str) -> bool:
    normalized_task = normalize_signal(task_status)
    normalized_robot_state = normalize_signal(robot_state)
    if normalized_task in MOP_MAINTENANCE_TASK_STATUSES:
        return True
    return any(fragment in normalized_robot_state for fragment in MOP_MAINTENANCE_STATE_FRAGMENTS)


def _is_dock_prep_state(robot_state: str, self_wash_base_status: str) -> bool:
    combined_state = f"{normalize_signal(robot_state)} {normalize_signal(self_wash_base_status)}"
    return any(fragment in combined_state for fragment in DOCK_PREP_STATE_FRAGMENTS)


def _is_post_run_maintenance_state(
    robot_state: str,
    self_wash_base_status: str,
) -> bool:
    combined_state = f"{normalize_signal(robot_state)} {normalize_signal(self_wash_base_status)}"
    return any(fragment in combined_state for fragment in POST_RUN_MAINTENANCE_STATE_FRAGMENTS)


def _is_dock_prep_paused(
    robot_state: str,
    self_wash_base_status: str,
    vacuum: State | None,
) -> bool:
    combined_state = f"{normalize_signal(robot_state)} {normalize_signal(self_wash_base_status)}"
    if "paused" in combined_state or "pause" in combined_state:
        return True

    return _vacuum_attributes_report_paused(vacuum)


def _is_dock_prep_resume_ready(clean_water_tank_status: str) -> bool:
    normalized_status = normalize_signal(clean_water_tank_status)
    return normalized_status in READY_WATER_TANK_STATES


def _vacuum_attributes_report_paused(state: State | None) -> bool:
    if state is None:
        return False
    return state.attributes.get("paused") is True and state.attributes.get("running") is False

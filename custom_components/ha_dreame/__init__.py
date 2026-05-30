"""HA Dreame integration scaffold."""

from __future__ import annotations

from datetime import datetime, timedelta
import logging
from pathlib import Path

from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryError
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
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
    VACUUM_DOMAIN,
)
from .queue_core import QueueState, new_state
from .runtime import HaDreameRuntimeData
from .runtime_observation import RuntimeObservationEntityIds
from .runtime_reconcile_runner import async_evaluate_and_apply_runtime_reconcile
from .runtime_state import QueueRunTracking
from .services import async_register_services, async_remove_services

_LOGGER = logging.getLogger(__name__)
PLATFORMS: list[Platform] = [Platform.SENSOR]
AUTO_RECONCILE_INTERVAL = timedelta(seconds=20)
FRONTEND_CARD_FILENAME = "ha-dreame-queue-card.js"
FRONTEND_STATIC_PATH = Path(__file__).parent / "frontend"
FRONTEND_STATIC_URL_PATH = f"/{DOMAIN}/frontend"
_FRONTEND_STATIC_REGISTERED = f"{DOMAIN}_frontend_static_registered"


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the integration from YAML."""
    hass.data.setdefault(DOMAIN, {})
    await _async_register_frontend_static_path(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up a config entry."""
    runtime_data = _build_runtime_data(hass, entry)

    hass.data.setdefault(DOMAIN, {})
    await _async_register_frontend_static_path(hass)
    async_register_services(hass)
    entry.runtime_data = runtime_data
    hass.data[DOMAIN][entry.entry_id] = entry
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    _register_auto_reconcile_interval(hass, entry)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    _LOGGER.info(
        "Loaded %s config entry %s for %s",
        DOMAIN,
        entry.entry_id,
        runtime_data.vacuum_entity_id,
    )
    return True


async def _async_register_frontend_static_path(hass: HomeAssistant) -> None:
    """Serve packaged frontend assets from a namespaced integration URL."""
    if hass.data.get(_FRONTEND_STATIC_REGISTERED):
        return

    await hass.http.async_register_static_paths(
        [
            StaticPathConfig(
                FRONTEND_STATIC_URL_PATH,
                str(FRONTEND_STATIC_PATH),
                False,
            )
        ]
    )
    hass.data[_FRONTEND_STATIC_REGISTERED] = True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if not unload_ok:
        return False

    hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    if hasattr(entry, "runtime_data"):
        del entry.runtime_data
    if not hass.data.get(DOMAIN):
        async_remove_services(hass)
    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload a config entry when options change."""
    await hass.config_entries.async_reload(entry.entry_id)


def _build_runtime_data(hass: HomeAssistant, entry: ConfigEntry) -> HaDreameRuntimeData:
    """Build validated runtime data for a config entry."""
    vacuum_entity_id = entry.data.get(CONF_VACUUM_ENTITY_ID)

    if not isinstance(vacuum_entity_id, str) or not vacuum_entity_id:
        raise ConfigEntryError("Config entry is missing a Dreame vacuum entity id")

    domain = vacuum_entity_id.split(".", maxsplit=1)[0]
    if domain != VACUUM_DOMAIN:
        raise ConfigEntryError(f"Configured Dreame entity is not a vacuum: {vacuum_entity_id}")

    registry_entry = er.async_get(hass).async_get(vacuum_entity_id)
    if registry_entry is None:
        raise ConfigEntryError(f"Configured Dreame vacuum does not exist: {vacuum_entity_id}")

    if registry_entry.platform != DREAME_VACUUM_DOMAIN:
        raise ConfigEntryError(f"Configured vacuum is not from Dreame: {vacuum_entity_id}")

    return HaDreameRuntimeData(
        auto_reconcile_enabled=entry.options.get(CONF_AUTO_RECONCILE_ENABLED) is True,
        commands_enabled=entry.options.get(CONF_ALLOW_ROBOT_COMMANDS) is True,
        observation_entity_ids=_build_observation_entity_ids(entry),
        queue_coordinator=_build_queue_coordinator(hass, entry),
        run_tracking_coordinator=_build_run_tracking_coordinator(hass, entry),
        vacuum_entity_id=vacuum_entity_id,
    )


def _register_auto_reconcile_interval(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Register automatic runtime reconciliation for explicitly enabled entries."""
    runtime_data = entry.runtime_data
    if not runtime_data.commands_enabled or not runtime_data.auto_reconcile_enabled:
        return

    @callback
    def _schedule_auto_reconcile(_now: datetime) -> None:
        hass.async_create_task(_async_auto_reconcile_tick(hass, entry))

    entry.async_on_unload(
        async_track_time_interval(
            hass,
            _schedule_auto_reconcile,
            AUTO_RECONCILE_INTERVAL,
        )
    )


async def _async_auto_reconcile_tick(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Run one automatic runtime reconcile pass."""
    if hass.data.get(DOMAIN, {}).get(entry.entry_id) is not entry:
        return

    runtime_data = entry.runtime_data
    if not runtime_data.commands_enabled or not runtime_data.auto_reconcile_enabled:
        return

    try:
        await async_evaluate_and_apply_runtime_reconcile(hass, runtime_data)
    except Exception:
        _LOGGER.exception(
            "Automatic %s reconcile failed for config entry %s",
            DOMAIN,
            entry.entry_id,
        )


def _build_observation_entity_ids(entry: ConfigEntry) -> RuntimeObservationEntityIds:
    """Build explicit observation entity ids from config entry options."""
    return RuntimeObservationEntityIds(
        task_status_entity_id=_optional_entity_id(entry.options.get(CONF_TASK_STATUS_ENTITY_ID)),
        robot_state_entity_id=_optional_entity_id(entry.options.get(CONF_ROBOT_STATE_ENTITY_ID)),
        current_room_entity_id=_optional_entity_id(entry.options.get(CONF_CURRENT_ROOM_ENTITY_ID)),
        error_entity_id=_optional_entity_id(entry.options.get(CONF_ERROR_ENTITY_ID)),
        cleaning_progress_entity_id=_optional_entity_id(
            entry.options.get(CONF_CLEANING_PROGRESS_ENTITY_ID)
        ),
        self_wash_base_status_entity_id=_optional_entity_id(
            entry.options.get(CONF_SELF_WASH_BASE_STATUS_ENTITY_ID)
        ),
        clean_water_tank_status_entity_id=_optional_entity_id(
            entry.options.get(CONF_CLEAN_WATER_TANK_STATUS_ENTITY_ID)
        ),
    )


def _optional_entity_id(value: object) -> str | None:
    """Return a stripped entity id option or None."""
    if not isinstance(value, str):
        return None
    entity_id = value.strip()
    return entity_id or None


def _build_queue_coordinator(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> DataUpdateCoordinator[QueueState]:
    """Build the runtime queue state coordinator for a config entry."""
    coordinator = DataUpdateCoordinator[QueueState](
        hass,
        _LOGGER,
        name=f"{DOMAIN}_{entry.entry_id}_queue",
    )
    coordinator.async_set_updated_data(new_state())
    return coordinator


def _build_run_tracking_coordinator(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> DataUpdateCoordinator[QueueRunTracking | None]:
    """Build the runtime run tracking coordinator for a config entry."""
    coordinator = DataUpdateCoordinator[QueueRunTracking | None](
        hass,
        _LOGGER,
        name=f"{DOMAIN}_{entry.entry_id}_run_tracking",
    )
    coordinator.async_set_updated_data(None)
    return coordinator

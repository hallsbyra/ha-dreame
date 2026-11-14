"""HA Dreame integration scaffold."""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
import logging
from pathlib import Path

from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import Event, EventStateChangedData, HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryError
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.event import (
    async_track_state_change_event,
    async_track_time_interval,
)
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    CONF_ALLOW_ROBOT_COMMANDS,
    CONF_AUTO_RECONCILE_ENABLED,
    CONF_VACUUM_ENTITY_ID,
    DOMAIN,
    DREAME_VACUUM_DOMAIN,
    VACUUM_DOMAIN,
)
from .queue_core import QueueState, new_state
from .audit import automatic_audit, register_external_command_audit
from .runtime import HaDreameRuntimeData
from .runtime_observation import ABSENT_STATES, RuntimeObservationEntityIds, normalize_signal
from .reconcile import async_reconcile_under_lock
from .runtime_state import QueueRunTracking
from .services import async_register_services, async_remove_services, async_start_waiting_queue

_LOGGER = logging.getLogger(__name__)
PLATFORMS: list[Platform] = [Platform.SENSOR]
AUTO_RECONCILE_INTERVAL = timedelta(seconds=20)
CONFIG_SCHEMA = cv.empty_config_schema(DOMAIN)
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
    entry.async_on_unload(register_external_command_audit(hass, runtime_data))
    hass.data[DOMAIN][entry.entry_id] = entry
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    _register_auto_reconcile_interval(hass, entry)
    _register_current_room_listener(hass, entry)
    _register_task_status_listener(hass, entry)
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
    runtime_data = getattr(entry, "runtime_data", None)
    if not isinstance(runtime_data, HaDreameRuntimeData):
        return False

    runtime_data.unload_requested.set()
    async with runtime_data.operation_lock:
        unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
        if not unload_ok:
            runtime_data.unload_requested.clear()
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
        observation_entity_ids=RuntimeObservationEntityIds.for_vacuum(
            vacuum_entity_id, entry.options
        ),
        operation_lock=asyncio.Lock(),
        queue_coordinator=_build_queue_coordinator(hass, entry),
        run_tracking_coordinator=_build_run_tracking_coordinator(hass, entry),
        unload_requested=asyncio.Event(),
        vacuum_entity_id=vacuum_entity_id,
    )


def _register_auto_reconcile_interval(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Register automatic runtime reconciliation for explicitly enabled entries."""
    runtime_data = entry.runtime_data
    if not runtime_data.commands_enabled or not runtime_data.auto_reconcile_enabled:
        return

    @callback
    def _schedule_auto_reconcile(_now: datetime) -> None:
        entry.async_create_task(
            hass,
            _async_auto_reconcile_tick(hass, entry),
            name=f"{DOMAIN} interval reconcile",
        )

    entry.async_on_unload(
        async_track_time_interval(
            hass,
            _schedule_auto_reconcile,
            AUTO_RECONCILE_INTERVAL,
        )
    )


def _register_task_status_listener(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> None:
    """Capture Dreame task lifecycle changes between interval ticks."""
    runtime_data = entry.runtime_data
    if not runtime_data.commands_enabled or not runtime_data.auto_reconcile_enabled:
        return

    task_status_entity_id = runtime_data.observation_entity_ids.task_status_entity_id

    @callback
    def _schedule_task_status_reconcile(event: Event[EventStateChangedData]) -> None:
        old_state = event.data["old_state"]
        new_state = event.data["new_state"]
        old_status = normalize_signal(old_state.state if old_state is not None else "")
        new_status = normalize_signal(new_state.state if new_state is not None else "")
        if new_status == old_status or new_status in ABSENT_STATES:
            return

        context = _active_reconcile_context(runtime_data)
        if context is None:
            return
        run_id, item_id = context
        entry.async_create_task(
            hass,
            _async_auto_reconcile_tick(
                hass,
                entry,
                expected_run_id=run_id,
                expected_item_id=item_id,
                task_status_override=new_status,
            ),
            name=f"{DOMAIN} task status reconcile",
        )

    entry.async_on_unload(
        async_track_state_change_event(
            hass,
            task_status_entity_id,
            _schedule_task_status_reconcile,
        )
    )


def _register_current_room_listener(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> None:
    """Capture room confirmations immediately instead of relying on interval polling."""
    runtime_data = entry.runtime_data
    if not runtime_data.commands_enabled or not runtime_data.auto_reconcile_enabled:
        return

    current_room_entity_id = runtime_data.observation_entity_ids.current_room_entity_id

    @callback
    def _schedule_current_room_reconcile(event: Event[EventStateChangedData]) -> None:
        old_state = event.data["old_state"]
        new_state = event.data["new_state"]
        if new_state is None or (
            old_state is not None
            and old_state.state == new_state.state
            and old_state.attributes == new_state.attributes
        ):
            return
        vacuum_state = hass.states.get(runtime_data.vacuum_entity_id)
        if vacuum_state is None or vacuum_state.state.lower() != "cleaning":
            return

        context = _active_reconcile_context(runtime_data)
        if context is None:
            return
        run_id, item_id = context
        entry.async_create_task(
            hass,
            _async_auto_reconcile_tick(
                hass,
                entry,
                expected_run_id=run_id,
                expected_item_id=item_id,
            ),
            name=f"{DOMAIN} current room reconcile",
        )

    entry.async_on_unload(
        async_track_state_change_event(
            hass,
            current_room_entity_id,
            _schedule_current_room_reconcile,
        )
    )


def _active_reconcile_context(runtime_data: HaDreameRuntimeData) -> tuple[str, str] | None:
    """Return the (run, item) whose completion the robot is being watched for."""
    item = runtime_data.awaited_item()
    run_id = runtime_data.queue_state.run_id
    if item is None or run_id is None:
        return None
    return run_id, item.item_id


async def _async_auto_reconcile_tick(
    hass: HomeAssistant,
    entry: ConfigEntry,
    *,
    expected_run_id: str | None = None,
    expected_item_id: str | None = None,
    task_status_override: str | None = None,
) -> None:
    """Run one automatic runtime reconcile pass."""
    runtime_data = getattr(entry, "runtime_data", None)
    if not isinstance(runtime_data, HaDreameRuntimeData):
        return

    async with runtime_data.operation_lock:
        if (
            hass.data.get(DOMAIN, {}).get(entry.entry_id) is not entry
            or getattr(entry, "runtime_data", None) is not runtime_data
            or runtime_data.unload_requested.is_set()
        ):
            return
        if expected_run_id is not None or expected_item_id is not None:
            if _active_reconcile_context(runtime_data) != (
                expected_run_id,
                expected_item_id,
            ):
                return

        try:
            with automatic_audit():
                if runtime_data.queue_state.run_state == "waiting_for_tanks":
                    await async_start_waiting_queue(hass, entry)
                    return
                await async_reconcile_under_lock(
                    hass,
                    runtime_data,
                    task_status_override=task_status_override,
                )
        except Exception:
            _LOGGER.exception(
                "Automatic %s reconcile failed for config entry %s",
                DOMAIN,
                entry.entry_id,
            )


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

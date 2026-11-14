"""Sensor entities for HA Dreame."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Event, EventStateChangedData, HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator

from .const import (
    ATTR_ALLOWED_ACTIONS,
    ATTR_BLOCKED_REASONS,
    ATTR_COMPLETED_ITEMS,
    ATTR_PENDING_ITEMS,
    ATTR_QUEUE_ITEMS,
    ATTR_RUNNING_ITEMS,
    ATTR_TOTAL_ITEMS,
    CONF_ALLOW_ROBOT_COMMANDS,
    CONF_CONFIG_ENTRY_ID,
    CONF_VACUUM_ENTITY_ID,
    SENSOR_QUEUE_STATUS,
    TITLE,
)
from .control_core import ControlState
from .queue_core import QueueState
from .queue_snapshot import count_queue_items, queue_item_snapshots
from .runtime import HaDreameRuntimeData


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up HA Dreame sensor entities for a config entry."""
    async_add_entities([HaDreameQueueStatusSensor(entry)])


class HaDreameQueueStatusSensor(CoordinatorEntity[DataUpdateCoordinator[QueueState]], SensorEntity):
    """Read-only status sensor for the HA Dreame queue.

    Besides the queue it publishes which queue actions the user may take now. Those depend
    on the robot too, so robot state changes that change them also write the state.
    """

    _attr_name = f"{TITLE} Queue Status"
    _attr_should_poll = False

    def __init__(self, entry: ConfigEntry) -> None:
        """Initialize the queue status sensor."""
        self._entry_id = entry.entry_id
        self._runtime_data: HaDreameRuntimeData
        self._runtime_data = entry.runtime_data
        super().__init__(self._runtime_data.queue_coordinator)
        self._attr_unique_id = f"{self._entry_id}_{SENSOR_QUEUE_STATUS}"
        self._published_control: ControlState | None = None

    async def async_added_to_hass(self) -> None:
        """Follow the robot entities that decide which actions are allowed."""
        await super().async_added_to_hass()
        self.async_on_remove(
            async_track_state_change_event(
                self.hass,
                self._runtime_data.observed_entity_ids,
                self._async_robot_state_changed,
            )
        )

    @callback
    def _async_robot_state_changed(self, event: Event[EventStateChangedData]) -> None:
        """Write state only when the robot change alters the allowed actions."""
        if self._runtime_data.control_state(self.hass) != self._published_control:
            self.async_write_ha_state()

    @property
    def native_value(self) -> str:
        """Return the current queue run state."""
        return self._queue_state.run_state

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return public-safe queue status attributes."""
        queue_state = self._queue_state
        control = self._runtime_data.control_state(self.hass)
        self._published_control = control
        return {
            CONF_ALLOW_ROBOT_COMMANDS: self._runtime_data.commands_enabled,
            CONF_CONFIG_ENTRY_ID: self._entry_id,
            CONF_VACUUM_ENTITY_ID: self._runtime_data.vacuum_entity_id,
            ATTR_PENDING_ITEMS: count_queue_items(queue_state, "pending"),
            ATTR_RUNNING_ITEMS: count_queue_items(queue_state, "running"),
            ATTR_COMPLETED_ITEMS: count_queue_items(queue_state, "completed"),
            ATTR_TOTAL_ITEMS: len(queue_state.items),
            ATTR_QUEUE_ITEMS: queue_item_snapshots(queue_state),
            ATTR_ALLOWED_ACTIONS: list(control.allowed_actions),
            ATTR_BLOCKED_REASONS: dict(control.blocked_reasons),
        }

    @property
    def _queue_state(self) -> QueueState:
        """Return the queue state from runtime data."""
        return self._runtime_data.queue_state

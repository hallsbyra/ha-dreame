"""Sensor entities for HA Dreame."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    ATTR_COMPLETED_ITEMS,
    ATTR_PENDING_ITEMS,
    ATTR_RUNNING_ITEMS,
    ATTR_TOTAL_ITEMS,
    CONF_VACUUM_ENTITY_ID,
    SENSOR_QUEUE_STATUS,
    TITLE,
)
from .queue_core import QueueState
from .runtime import HaDreameRuntimeData


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up HA Dreame sensor entities for a config entry."""
    async_add_entities([HaDreameQueueStatusSensor(entry)])


class HaDreameQueueStatusSensor(SensorEntity):
    """Read-only status sensor for the HA Dreame queue."""

    _attr_name = f"{TITLE} Queue Status"
    _attr_should_poll = False

    def __init__(self, entry: ConfigEntry) -> None:
        """Initialize the queue status sensor."""
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_{SENSOR_QUEUE_STATUS}"

    @property
    def native_value(self) -> str:
        """Return the current queue run state."""
        return self._queue_state.run_state

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return public-safe queue status attributes."""
        queue_state = self._queue_state
        return {
            CONF_VACUUM_ENTITY_ID: self._runtime_data.vacuum_entity_id,
            ATTR_PENDING_ITEMS: _count_items(queue_state, "pending"),
            ATTR_RUNNING_ITEMS: _count_items(queue_state, "running"),
            ATTR_COMPLETED_ITEMS: _count_items(queue_state, "completed"),
            ATTR_TOTAL_ITEMS: len(queue_state.items),
        }

    @property
    def _runtime_data(self) -> HaDreameRuntimeData:
        """Return typed runtime data for the config entry."""
        return self._entry.runtime_data

    @property
    def _queue_state(self) -> QueueState:
        """Return the queue state from runtime data."""
        return self._runtime_data.queue_state


def _count_items(queue_state: QueueState, status: str) -> int:
    """Count queue items with one status."""
    return sum(item.status == status for item in queue_state.items)

"""Shared test helpers for HA Dreame."""

from dataclasses import replace

from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.ha_dreame.const import DOMAIN, DREAME_VACUUM_DOMAIN, TITLE


def register_entity(
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


def mock_entry(
    data: dict[str, str],
    *,
    options: dict[str, object] | None = None,
    version: int = 1,
) -> MockConfigEntry:
    """Build a mock HA Dreame config entry."""
    return MockConfigEntry(domain=DOMAIN, title=TITLE, data=data, options=options, version=version)


def set_dispatch(runtime_data, dispatch) -> None:
    """Attach dispatch tracking to the runtime's current queue state."""
    runtime_data.set_queue_state(replace(runtime_data.queue_state, dispatch=dispatch))


def without_dispatch(queue_state):
    """Return a queue state for comparisons that ignore its dispatch tracking."""
    return replace(queue_state, dispatch=None)

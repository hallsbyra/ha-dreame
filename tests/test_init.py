"""Tests for HA Dreame integration setup."""

from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.ha_dreame.const import DOMAIN, TITLE


async def test_setup_and_unload_entry(hass: HomeAssistant) -> None:
    """Test that a config entry sets up and unloads cleanly."""
    entry = MockConfigEntry(domain=DOMAIN, title=TITLE, data={})
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert hass.data[DOMAIN][entry.entry_id] == {"status": "scaffold"}

    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()

    assert entry.entry_id not in hass.data[DOMAIN]

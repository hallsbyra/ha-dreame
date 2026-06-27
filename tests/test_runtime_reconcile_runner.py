"""Tests for shared runtime reconcile runner behavior."""

import pytest

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from _pytest.monkeypatch import MonkeyPatch

from custom_components.ha_dreame.const import CONF_ALLOW_ROBOT_COMMANDS, CONF_VACUUM_ENTITY_ID
from custom_components.ha_dreame.queue_core import QueueError
from custom_components.ha_dreame.runtime_reconcile_runner import (
    async_evaluate_and_apply_runtime_reconcile,
)

from .helpers import mock_entry, register_entity

pytestmark = pytest.mark.usefixtures("mock_dreame_vacuum_dependency")


async def test_runtime_reconcile_runner_translates_queue_errors(
    hass: HomeAssistant,
    monkeypatch: MonkeyPatch,
) -> None:
    """Test pure queue errors become Home Assistant service errors."""
    vacuum_entity_id = register_entity(hass, "vacuum.dreame_robot")
    entry = mock_entry(
        {CONF_VACUUM_ENTITY_ID: vacuum_entity_id},
        options={CONF_ALLOW_ROBOT_COMMANDS: True},
    )
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    def _raise_queue_error(*_args: object, **_kwargs: object) -> object:
        raise QueueError("queue failed")

    monkeypatch.setattr(
        "custom_components.ha_dreame.runtime_reconcile_runner.apply_reconcile_decision",
        _raise_queue_error,
    )

    with pytest.raises(HomeAssistantError, match="queue failed"):
        await async_evaluate_and_apply_runtime_reconcile(hass, entry.runtime_data)

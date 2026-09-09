"""Bounded command provenance, separate from robot state and queue semantics."""

from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from datetime import UTC, datetime
import logging
from typing import Any

from homeassistant.core import (
    Context,
    Event,
    EventStateChangedData,
    HomeAssistant,
    ServiceCall,
    callback,
)
from homeassistant.helpers.event import async_track_state_change_event

from .const import DOMAIN
from .runtime import HaDreameRuntimeData

_LOGGER = logging.getLogger(__name__)
_CALL: ContextVar[ServiceCall | None] = ContextVar("ha_dreame_audit_call", default=None)


def record_activity(
    runtime: HaDreameRuntimeData,
    action: str,
    outcome: str,
    *,
    context: Context,
    source: str,
    room_id: int | None = None,
    item_id: str | None = None,
    reason: str | None = None,
) -> None:
    """Record only allowlisted metadata; never arbitrary service payloads or errors."""
    queue_item = next(
        (
            item
            for item in runtime.queue_state.items
            if item.item_id == (item_id or runtime.queue_state.current_item_id)
        ),
        None,
    )
    if queue_item is None:
        queue_item = next(
            (item for item in runtime.queue_state.items if item.status == "pending"), None
        )
    event = {
        "time": datetime.now(UTC).isoformat(),
        "action": action,
        "outcome": outcome,
        "source": source,
        "context_id": context.id,
        "parent_id": context.parent_id,
        "user_id": context.user_id,
        "run_id": runtime.queue_state.run_id,
        "queue_state": runtime.queue_state.run_state,
        "item_id": item_id or (queue_item.item_id if queue_item else None),
        "room_id": room_id if room_id is not None else (queue_item.room_id if queue_item else None),
        "reason": reason,
    }
    runtime.recent_activity.append(event)
    _LOGGER.info("HA Dreame audit vacuum=%s event=%s", runtime.vacuum_entity_id, event)


def _source(context: Context) -> str:
    if context.user_id:
        return "user"
    return "context_chain" if context.parent_id else "unknown"


@contextmanager
def automatic_audit():
    """Do not inherit a service caller when an event schedules background recovery."""
    token = _CALL.set(None)
    try:
        yield
    finally:
        _CALL.reset(token)


@contextmanager
def service_audit(runtime: HaDreameRuntimeData, call: ServiceCall | None):
    """Correlate accepted/rejected queue mutations with their caller and commands."""
    if call is None:
        yield
        return
    token = _CALL.set(call)
    before = {item.item_id for item in runtime.queue_state.items}
    details = {
        "context": call.context,
        "source": _source(call.context),
        "room_id": call.data.get("room_id"),
    }
    record_activity(runtime, call.service, "requested", **details)
    try:
        yield
    except Exception as err:
        record_activity(runtime, call.service, "rejected", reason=type(err).__name__, **details)
        raise
    else:
        added = next(
            (item for item in runtime.queue_state.items if item.item_id not in before), None
        )
        record_activity(
            runtime, call.service, "accepted", item_id=added.item_id if added else None, **details
        )
    finally:
        _CALL.reset(token)


async def async_call_robot_service(
    hass: HomeAssistant,
    domain: str,
    service: str,
    data: dict[str, Any],
    *,
    blocking: bool = True,
) -> None:
    """Send a command with provenance and distinguish acceptance from physical start."""
    call = _CALL.get()
    context = call.context if call else Context()
    source = f"ha_dreame.{call.service}" if call else "automatic_reconcile"
    runtime = next(
        (
            entry.runtime_data
            for entry in hass.data.get(DOMAIN, {}).values()
            if entry.runtime_data.vacuum_entity_id == data.get("entity_id")
        ),
        None,
    )
    action = f"{domain}.{service}"
    if runtime is not None:
        record_activity(runtime, action, "requested", context=context, source=source)
    try:
        await hass.services.async_call(domain, service, data, blocking=blocking, context=context)
    except Exception as err:
        if runtime is not None:
            record_activity(
                runtime,
                action,
                "rejected",
                context=context,
                source=source,
                reason=type(err).__name__,
            )
        raise
    else:
        if runtime is not None:
            record_activity(runtime, action, "accepted", context=context, source=source)


def register_external_command_audit(hass: HomeAssistant, runtime: HaDreameRuntimeData):
    """Observe direct HA robot calls too; service events are requests, not successes."""

    @callback
    def observe(event: Event) -> None:
        domain = event.data.get("domain")
        if domain not in {"vacuum", "dreame_vacuum"}:
            return
        data = event.data.get("service_data", {})
        targets = data.get("entity_id", [])
        if isinstance(targets, str):
            targets = targets.split(",")
        if runtime.vacuum_entity_id not in targets:
            return
        action = f"{domain}.{event.data.get('service')}"
        if any(
            item["context_id"] == event.context.id
            and item["action"] == action
            and item["outcome"] == "requested"
            and (item["source"].startswith("ha_dreame.") or item["source"] == "automatic_reconcile")
            for item in runtime.recent_activity
        ):
            return
        record_activity(
            runtime,
            action,
            "observed_request",
            context=event.context,
            source=_source(event.context),
        )

    @callback
    def observe_task(event: Event[EventStateChangedData]) -> None:
        old_state = event.data.get("old_state")
        new_state = event.data.get("new_state")
        if new_state is None or (old_state is not None and old_state.state == new_state.state):
            return
        record_activity(
            runtime,
            "robot_task_status",
            "observed",
            context=event.context,
            source="robot_observation",
            reason=new_state.state,
        )

    task_entity = runtime.observation_entity_ids.task_status_entity_id or (
        "sensor." + runtime.vacuum_entity_id.split(".", 1)[1] + "_task_status"
    )
    unsubscribe_commands = hass.bus.async_listen("call_service", observe)
    unsubscribe_tasks = async_track_state_change_event(hass, [task_entity], observe_task)

    @callback
    def unsubscribe() -> None:
        unsubscribe_commands()
        unsubscribe_tasks()

    return unsubscribe

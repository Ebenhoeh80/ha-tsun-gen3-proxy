"""MQTT-Koordinator für die TSUN-Inverter-Integration."""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

from homeassistant.components import mqtt
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, LOGGER, TOPIC_PREFIX
from .parser import extract_values, format_state, parse_topic, spec_for_key

_LOGGER = logging.getLogger(LOGGER)

DataT = dict[str, dict[str, Any]]


class TsunCoordinator(DataUpdateCoordinator[DataT]):
    """Hält die neuesten Messwerte aller Knoten des Proxys vor."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialisiert den Koordinator ohne Polling-Intervall."""
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=None,
        )
        self.entry_id = entry.entry_id
        self._unsubscribe: Callable[[], None] | None = None

    async def async_setup(self) -> None:
        """Abonniert alle Topics des Proxys über die HA-MQTT-Integration."""
        self._unsubscribe = await mqtt.async_subscribe(
            self.hass,
            f"{TOPIC_PREFIX}/#",
            self._handle_message,
        )
        _LOGGER.debug("Abonniert: %s/#", TOPIC_PREFIX)

    async def _async_update_data(self) -> DataT:
        """Liefert den aktuellen Datenstand (Push, kein Polling)."""
        return self.data if self.data is not None else {}

    @callback
    def _handle_message(self, message: Any) -> None:
        """Verarbeitet eine eingehende MQTT-Nachricht."""
        parsed = parse_topic(str(message.topic))
        if parsed is None:
            return
        node_id, _group = parsed

        updates: dict[str, Any] = {}
        for key, raw_value in extract_values(message.payload).items():
            spec = spec_for_key(key)
            if spec is None:
                continue
            state = format_state(raw_value, spec)
            if state is not None:
                updates[spec.suffix] = state

        if not updates:
            return

        data: DataT = dict(self.data or {})
        values = dict(data.get(node_id, {}))
        values.update(updates)
        data[node_id] = values
        self.async_set_updated_data(data)

    async def async_unload(self) -> None:
        """Beendet das MQTT-Abonnement."""
        if self._unsubscribe is not None:
            self._unsubscribe()
            self._unsubscribe = None

    async def async_send_command(self, node_id: str, topic: str, value: str) -> None:
        """Veröffentlicht einen Befehl für einen Knoten."""
        await mqtt.async_publish(
            self.hass,
            f"{TOPIC_PREFIX}/{node_id}/{topic}",
            value,
            retain=True,
        )

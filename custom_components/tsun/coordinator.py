"""MQTT-Koordinator für die TSUN-Inverter-Integration."""

from __future__ import annotations

import logging
import time
from collections.abc import Callable
from typing import Any

from homeassistant.components import mqtt
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryNotReady, HomeAssistantError
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    CONF_NODE_ID,
    DOMAIN,
    LOGGER,
    MAX_NODES,
    STALE_TIMEOUT_SECONDS,
    TOPIC_PREFIX,
)
from .parser import (
    discovered_nodes,
    extract_values,
    format_state,
    parse_topic,
    spec_for_key,
)

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
        self.configured_node: str | None = entry.data.get(CONF_NODE_ID)
        self._unsubscribe: Callable[[], None] | None = None
        self._last_seen: dict[str, float] = {}
        self._last_seen_wall: dict[str, float] = {}

    async def async_setup(self) -> None:
        """Abonniert alle Topics des Proxys über die HA-MQTT-Integration.

        Laut Home-Assistant-Vorgabe muss vor dem eigenen Abonnieren auf den
        MQTT-Client gewartet werden: `dependencies` lädt die MQTT-Integration,
        garantiert aber nicht, dass deren Config Entry schon verbunden ist.
        Ohne das Warten gehen beim Neustart die ersten Messwerte verloren.
        """
        if not await mqtt.async_wait_for_mqtt_client(self.hass):
            raise ConfigEntryNotReady("MQTT-Client nicht verfügbar")
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
    def new_nodes(self, known: set[str], exclude_proxy: bool = False) -> set[str]:
        """Liefert noch nicht registrierte Knoten, begrenzt und deterministisch.

        Diese gemeinsame Implementierung ersetzt die fünf duplizierten
        Listener in den Plattformen (A-28).
        """
        nodes = discovered_nodes(self.data, self.configured_node)
        if exclude_proxy:
            nodes.discard("proxy")
        return nodes - known

    def last_seen(self, node_id: str) -> float | None:
        """Zeitpunkt der letzten Nachricht eines Knotens (monoton)."""
        return self._last_seen.get(node_id)

    def last_seen_wall(self, node_id: str) -> float | None:
        """Wall-Clock-Zeitpunkt der letzten Nachricht (für Diagnostics)."""
        return self._last_seen_wall.get(node_id)

    def is_stale(self, node_id: str) -> bool:
        """Meldet, ob ein Knoten länger als zulässig keine Nachricht sandte."""
        seen = self._last_seen.get(node_id)
        return seen is None or time.monotonic() - seen > STALE_TIMEOUT_SECONDS

    @callback
    def _handle_message(self, message: Any) -> None:
        """Verarbeitet eine eingehende MQTT-Nachricht."""
        topic = str(message.topic)
        parsed = parse_topic(topic)
        if parsed is None:
            _LOGGER.debug("Ignoriere fremdes Topic: %s", topic)
            return
        node_id, group = parsed

        # Auch Nachrichten ohne bekannte Messwerte gelten als Lebenszeichen
        # (Upstream-Heartbeat 120 s). Damit bleibt ein Knoten verfügbar, solange
        # der Proxy erreichbar ist (A-21).
        self._last_seen[node_id] = time.monotonic()
        self._last_seen_wall[node_id] = time.time()

        existing = self.data or {}
        if node_id not in existing and len(existing) >= MAX_NODES:
            if node_id != self.configured_node:
                _LOGGER.warning(
                    "Knoten %s auf %s/# ignoriert: Maximum von %s erreicht",
                    node_id,
                    TOPIC_PREFIX,
                    MAX_NODES,
                )
                return

        updates: dict[str, Any] = {}
        unknown: set[str] = set()
        for key, raw_value in extract_values(message.payload).items():
            spec = spec_for_key(key, group)
            if spec is None:
                unknown.add(key)
                continue
            state = format_state(raw_value, spec)
            if state is None:
                _LOGGER.debug("Verwerfe Wert für %s/%s: ungültig", node_id, key)
                continue
            updates[spec.suffix] = state

        if not updates:
            if unknown:
                _LOGGER.debug(
                    "Keine bekannten Messwerte in %s (unbekannte Keys: %s)",
                    topic,
                    sorted(unknown)[:10],
                )
            return

        data: DataT = dict(existing)
        values = dict(data.get(node_id, {}))
        values.update(updates)
        data[node_id] = values

        # Nur noch erlaubte Knoten behalten, damit die Obergrenze auch nach
        # einem Neustart mit retains nicht überschritten wird.
        allowed = discovered_nodes(data, self.configured_node)
        self._last_seen = {
            node: seen for node, seen in self._last_seen.items() if node in allowed
        }
        self._last_seen_wall = {
            node: seen for node, seen in self._last_seen_wall.items() if node in allowed
        }
        self.async_set_updated_data(
            {node: data[node] for node in allowed if node in data}
        )

    async def async_unload(self) -> None:
        """Beendet das MQTT-Abonnement."""
        if self._unsubscribe is not None:
            self._unsubscribe()
            self._unsubscribe = None

    async def async_send_command(self, node_id: str, topic: str, value: str) -> bool:
        """Veröffentlicht einen Befehl für einen Knoten.

        QoS 0 und ``retain=False`` sind für Telemetrie-/Steuerbefehle korrekt.
        Bei einem Publish-Fehler wird der Aufrufer informiert, statt den Wert
        optimistisch in der UI zu setzen (A-23).
        """
        try:
            await mqtt.async_publish(
                self.hass,
                f"{TOPIC_PREFIX}/{node_id}/{topic}",
                value,
                retain=False,
            )
        except (HomeAssistantError, ValueError) as err:
            _LOGGER.error(
                "Befehl %s/%s konnte nicht gesendet werden: %s", node_id, topic, err
            )
            return False
        return True

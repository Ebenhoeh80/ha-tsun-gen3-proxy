"""Diagnoseausgabe für die TSUN-Inverter-Integration."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.core import HomeAssistant

from . import TsunConfigEntry
from .const import (
    CONF_MQTT_HOST,
    CONF_MQTT_PASSWORD,
    CONF_MQTT_USER,
    PLATFORMS,
    STALE_TIMEOUT_SECONDS,
    VERSION,
)
from .coordinator import TsunCoordinator

_TO_REDACT = {CONF_MQTT_HOST, CONF_MQTT_PASSWORD, CONF_MQTT_USER}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: TsunConfigEntry
) -> dict[str, Any]:
    """Liefert eine Diagnoseausgabe ohne Zugangsdaten oder Hostnamen.

    Ergänzt wurden Laufzeitdetails, die fehlen, wenn – wie beim Live-Check –
    kein MQTT-Datenstrom ankommt: letzte Nachricht pro Knoten, Alter und
    Flags für veraltete Knoten (A-12).
    """
    coordinator: TsunCoordinator = entry.runtime_data
    nodes = coordinator.data or {}
    now = datetime.now(UTC)
    node_details: dict[str, Any] = {}
    for node_id, values in sorted(nodes.items()):
        seen = coordinator.last_seen_wall(node_id)
        node_details[node_id] = {
            "values": dict(values),
            "last_seen": datetime.fromtimestamp(seen, UTC).isoformat()
            if seen
            else None,
            "age_seconds": round(now.timestamp() - seen, 1) if seen else None,
            "stale": coordinator.is_stale(node_id),
        }

    return {
        "version": VERSION,
        "integration": "tsun",
        "config_entry": {
            "entry_id": "**REDACTED**",
            "title": entry.title,
            "unique_id": "**REDACTED**" if entry.unique_id else None,
            "data": async_redact_data(dict(entry.data), _TO_REDACT),
            "options": async_redact_data(dict(entry.options), _TO_REDACT),
        },
        "platforms": list(PLATFORMS),
        "stale_timeout_seconds": STALE_TIMEOUT_SECONDS,
        "nodes": node_details,
    }

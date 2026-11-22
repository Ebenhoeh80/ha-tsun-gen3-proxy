"""Diagnoseausgabe für die TSUN-Inverter-Integration."""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import (
    CONF_MQTT_HOST,
    CONF_MQTT_PASSWORD,
    CONF_MQTT_USER,
    DOMAIN,
    PLATFORMS,
    VERSION,
)
from .coordinator import TsunCoordinator

_TO_REDACT = {CONF_MQTT_HOST, CONF_MQTT_PASSWORD, CONF_MQTT_USER}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Liefert eine Diagnoseausgabe ohne Zugangsdaten oder Hostnamen."""
    coordinator: TsunCoordinator = hass.data[DOMAIN][entry.entry_id]
    return {
        "version": VERSION,
        "integration": DOMAIN,
        "config_entry": {
            "title": entry.title,
            "unique_id": "**redacted**" if entry.unique_id else None,
            "data": async_redact_data(dict(entry.data), _TO_REDACT),
            "options": async_redact_data(dict(entry.options), _TO_REDACT),
        },
        "platforms": list(PLATFORMS),
        "nodes": sorted((coordinator.data or {}).keys()),
    }

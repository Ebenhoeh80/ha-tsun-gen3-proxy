"""Diagnoseausgabe für die TSUN-Inverter-Integration."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import CONF_MQTT_PASSWORD, DOMAIN, PLATFORMS, VERSION
from .coordinator import TsunCoordinator


def _redact(data: dict[str, Any]) -> dict[str, Any]:
    """Entfernt Geheimniswerte aus einer Konfiguration."""
    return {
        key: "**redacted**" if key == CONF_MQTT_PASSWORD else value
        for key, value in data.items()
    }


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Liefert eine Diagnoseausgabe ohne Passwörter."""
    coordinator: TsunCoordinator = hass.data[DOMAIN][entry.entry_id]
    return {
        "version": VERSION,
        "integration": DOMAIN,
        "config_entry": {
            "title": entry.title,
            "unique_id": entry.unique_id,
            "data": _redact(dict(entry.data)),
            "options": dict(entry.options),
        },
        "platforms": list(PLATFORMS),
        "nodes": sorted((coordinator.data or {}).keys()),
    }

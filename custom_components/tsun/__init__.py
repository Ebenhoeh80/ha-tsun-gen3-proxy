"""TSUN Inverter Home Assistant integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntry

from .const import (
    CONF_LATEST_VERSION,
    CONF_MQTT_HOST,
    CONF_MQTT_PASSWORD,
    CONF_MQTT_USER,
    DOMAIN,
    LOGGER,
    PLATFORMS,
)
from .coordinator import TsunCoordinator
from .parser import discovered_nodes, sanitize

_LOGGER = logging.getLogger(LOGGER)

type TsunConfigEntry = ConfigEntry[TsunCoordinator]

# Legacy-Schlüssel aus v0.1/v0.2, die heute nicht mehr benötigt werden.
_LEGACY_KEYS = (CONF_MQTT_HOST, CONF_MQTT_USER, CONF_MQTT_PASSWORD, CONF_LATEST_VERSION)


async def async_migrate_entry(hass: HomeAssistant, entry: TsunConfigEntry) -> bool:
    """Entfernt nicht mehr benötigte Zugangsdaten aus dem Config Entry.

    Die MQTT-Zugangsdaten der ersten Versionen werden von der HA-eigenen
    MQTT-Integration verwaltet. Sie lagen nur selbstredundant im Storage und
    sind dort aus Datenschutzgründen zu entfernen (A-19).
    """
    if not any(key in entry.data for key in _LEGACY_KEYS):
        return True
    new_data = {
        key: value for key, value in entry.data.items() if key not in _LEGACY_KEYS
    }
    hass.config_entries.async_update_entry(entry, data=new_data)
    _LOGGER.info("Veraltete Konfigurationsschlüssel entfernt: %s", entry.entry_id)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: TsunConfigEntry) -> bool:
    """Set up TSUN Inverter from a config entry."""
    coordinator = TsunCoordinator(hass, entry)
    await coordinator.async_setup()
    await coordinator.async_config_entry_first_refresh()

    # HA-Empfehlung: Laufzeitdaten am Entry, nicht in hass.data (A-11).
    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    _LOGGER.info("TSUN Inverter %s initialisiert", entry.entry_id)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: TsunConfigEntry) -> bool:
    """Unload a config entry."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        await entry.runtime_data.async_unload()
    return unloaded


async def async_remove_config_entry_device(
    hass: HomeAssistant, entry: TsunConfigEntry, device_entry: DeviceEntry
) -> bool:
    """Erlaubt nur das Entfernen von Geräten ohne aktiven Knoten.

    HA fordert diesen Hook für ``stale-devices``. Es werden bewusst keine
    Geräte automatisch gelöscht: der Nutzer entscheidet, welche verwaisten
    Geräte entfernt werden (A-14).
    """
    coordinator = entry.runtime_data
    active = discovered_nodes(coordinator.data, coordinator.configured_node)
    for identifier in device_entry.identifiers:
        if identifier[0] != DOMAIN:
            continue
        if any(identifier[1] == sanitize(node) for node in active):
            return False
    return True


async def _async_update_listener(hass: HomeAssistant, entry: TsunConfigEntry) -> None:
    """Reload the entry after options changed."""
    await hass.config_entries.async_reload(entry.entry_id)

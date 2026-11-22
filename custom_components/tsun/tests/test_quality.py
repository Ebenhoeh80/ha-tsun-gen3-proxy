"""Tests für Availability, Diagnostics, Migration und Device-Removal."""

from __future__ import annotations

import asyncio
import time
from unittest.mock import MagicMock

from homeassistant.components.sensor import SensorDeviceClass

from custom_components.tsun import async_migrate_entry, async_remove_config_entry_device
from custom_components.tsun.const import (
    CONF_LATEST_VERSION,
    CONF_MQTT_HOST,
    CONF_MQTT_PASSWORD,
    CONF_MQTT_USER,
    VERSION,
)
from custom_components.tsun.diagnostics import async_get_config_entry_diagnostics
from custom_components.tsun.entity import TsunEntity
from custom_components.tsun.sensor import TsunSensor
from custom_components.tsun.tests.helpers import make_coordinator, make_entry, spec


def test_runtime_data_lesbar() -> None:
    """Der Koordinator liegt am Config Entry, nicht in hass.data."""
    coordinator = make_coordinator()
    entry = make_entry(runtime_data=coordinator)
    assert entry.runtime_data is coordinator


def test_entitaet_ist_bei_frischem_knoten_verfuegbar() -> None:
    """Ein Knoten mit aktuellem Heartbeat gilt als verfügbar."""
    coordinator = make_coordinator(nodes=("inv_1",))
    coordinator._last_seen["inv_1"] = time.monotonic()
    entity = TsunSensor(coordinator, "entry1", "inv_1", spec("rated_power"))
    assert entity.available is True
    assert entity._attr_device_class is SensorDeviceClass.POWER


def test_entitaet_wird_bei_stalem_knoten_unverfuegbar() -> None:
    """Nach dem Timeout zeigt HA veraltete Werte nicht mehr als verfügbar."""
    coordinator = make_coordinator(nodes=("inv_1",))
    coordinator._last_seen["inv_1"] = time.monotonic() - 500
    entity = TsunSensor(coordinator, "entry1", "inv_1", spec("rated_power"))
    assert entity.available is False


def test_entitaet_nutzt_translation_key() -> None:
    """Namen und Icons kommen aus den Übersetzungsdateien."""
    coordinator = make_coordinator(nodes=("inv_1",))
    entity = TsunEntity(coordinator, "entry1", "inv_1", spec("rated_power"))
    assert entity._attr_translation_key == "rated_power"


def test_remove_device_nur_fuer_inaktive_knoten() -> None:
    """Die Registry darf aktive Geräte nicht löschen, verwaiste schon."""
    coordinator = make_coordinator(nodes=("inv_1",))
    entry = make_entry(runtime_data=coordinator)
    device = MagicMock()

    device.identifiers = {("tsun", "inv_1")}
    assert (
        asyncio.run(async_remove_config_entry_device(MagicMock(), entry, device))
        is False
    )

    device.identifiers = {("tsun", "alter_knoten")}
    assert (
        asyncio.run(async_remove_config_entry_device(MagicMock(), entry, device))
        is True
    )


def test_diagnostics_redaction() -> None:
    """Zugangsdaten und Hostname erscheinen nie in der Diagnoseausgabe."""
    coordinator = make_coordinator(nodes=("inv_1",))
    entry = make_entry(
        data={
            CONF_MQTT_HOST: "geheim.example.org",
            CONF_MQTT_USER: "geheimnutzer",
            CONF_MQTT_PASSWORD: "geheimpasswort",
        },
        runtime_data=coordinator,
    )
    result = asyncio.run(async_get_config_entry_diagnostics(MagicMock(), entry))
    text = str(result)
    assert "geheim.example.org" not in text
    assert "geheimnutzer" not in text
    assert "geheimpasswort" not in text
    assert "**REDACTED**" in text
    assert result["version"] == VERSION
    assert "inv_1" in result["nodes"]


def test_migration_entfernt_legacy_schluessel() -> None:
    """Alte MQTT-Zugangsdaten und der Options-Default wandern nicht weiter."""
    hass = MagicMock()
    entry = make_entry(
        data={
            CONF_MQTT_HOST: "alt",
            CONF_MQTT_USER: "alt",
            CONF_MQTT_PASSWORD: "alt",
            CONF_LATEST_VERSION: "0.2.4",
            "node_id": "inv_1",
        }
    )
    assert asyncio.run(async_migrate_entry(hass, entry)) is True
    new_data = hass.config_entries.async_update_entry.call_args.kwargs["data"]
    assert new_data == {"node_id": "inv_1"}

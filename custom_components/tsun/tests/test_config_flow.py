"""Tests für Topic-Auflösung, Payload und MQTT-Verfügbarkeit im Flow."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from custom_components.tsun.config_flow import TsunConfigFlow
from custom_components.tsun.parser import extract_values, parse_topic


def test_parse_topic_upstream_format():
    """Das Standardformat des Proxys wird korrekt zerlegt."""
    assert parse_topic("tsun/inv_1/total") == ("inv_1", "total")
    assert parse_topic("tsun/proxy/proxy") == ("proxy", "proxy")


def test_parse_topic_legacy_format():
    """Das ältere Format mit doppelten Schrägstrichen bleibt lesbar."""
    assert parse_topic("tsun//inv_1//total") == ("inv_1", "total")


def test_parse_topic_ignoriert_andere_prefixe():
    """Discovery- und fremde Topics dürfen nicht verarbeitet werden."""
    assert parse_topic("homeassistant/sensor/tsun/config") is None
    assert parse_topic("tsun") is None


def test_extract_values_json():
    """Proxy-Payloads sind JSON-Objekte mit Messwert-Schlüsseln."""
    assert extract_values(b'{"Daily_Generation": 1.23}') == {
        "Daily_Generation": 1.23
    }


def test_extract_values_verschachtelt():
    """Verschachtelte Payloads werden auf oberste Schlüssel abgeflacht."""
    payload = b'{"pv1": {"Daily_Generation": 4.2, "Total_Generation": 10}}'
    assert extract_values(payload) == {
        "Daily_Generation": 4.2,
        "Total_Generation": 10,
    }


def test_extract_values_zahl_und_leer():
    """Alte Zahlen-Payloads landen unter ``value``, leere ergeben nichts."""
    assert extract_values("42.5") == {"value": 42.5}
    assert extract_values("") == {}
    assert extract_values(b"n/a") == {"value": "n/a"}


def _flow() -> MagicMock:
    """Minimaler Flow-Ersatz: nur die vom Schritt genutzten Methoden."""
    flow = MagicMock()
    flow._async_current_entries.return_value = []
    flow.async_set_unique_id = AsyncMock()
    flow.async_abort.return_value = {"type": "abort", "reason": "mqtt_unavailable"}
    flow.async_create_entry.return_value = {"type": "create_entry", "data": {}}
    return flow


def test_bestaetigung_bricht_ohne_mqtt_ab() -> None:
    """Ohne MQTT-Client gibt es eine klare Meldung statt Setup-Fehler."""
    flow = _flow()
    with patch(
        "custom_components.tsun.config_flow.async_wait_for_mqtt_client",
        new=AsyncMock(return_value=False),
    ):
        result = asyncio.run(TsunConfigFlow.async_step_user(flow, {}))
    assert result["reason"] == "mqtt_unavailable"
    flow.async_abort.assert_called_once_with(reason="mqtt_unavailable")
    flow.async_create_entry.assert_not_called()


def test_bestaetigung_erstellt_entry_mit_mqtt() -> None:
    """Mit verfügbarem MQTT-Client bleibt die Einrichtung ein Klick."""
    flow = _flow()
    with patch(
        "custom_components.tsun.config_flow.async_wait_for_mqtt_client",
        new=AsyncMock(return_value=True),
    ):
        result = asyncio.run(TsunConfigFlow.async_step_user(flow, {}))
    assert result["type"] == "create_entry"
    flow.async_create_entry.assert_called_once_with(title="TSUN Inverter", data={})

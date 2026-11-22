"""Tests für Topic-Auflösung und Payload-Auswertung (ohne HA-Laufzeit)."""

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

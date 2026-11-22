"""Tests für die Entitätszuordnung der TSUN-Integration (ohne HA-Laufzeit)."""

from custom_components.tsun.parser import (
    ENTITY_SPECS,
    device_info,
    format_state,
    spec_for_key,
    unique_id,
)


def test_entity_specs_decken_alle_proxy_werte_ab():
    """Die relevanten Messwerte des Proxys müssen eine Entität haben."""
    keys = {key for spec in ENTITY_SPECS for key in spec.keys}
    assert {
        "Rated_Power",
        "Daily_Generation",
        "Total_Generation",
        "SW_Exception",
        "AT_Command_Blocked",
    } <= keys


def test_spec_for_key_findet_aliase():
    """Sowohl Upstream- als auch Legacy-Schlüssel werden erkannt."""
    assert spec_for_key("Rated_Power") is not None
    assert spec_for_key("rated_power") is not None
    assert spec_for_key("gibts_nicht") is None


def test_unique_id_ist_stabil():
    """Eindeutige IDs dürfen sich bei Leerzeichen nicht ändern."""
    spec = spec_for_key("Daily_Generation")
    assert spec is not None
    assert unique_id("entry1", "inv 1", spec) == "entry1_inv_1_total_generation_today"


def test_format_state_numerisch_und_binaer():
    """Zahlen und Binärzustände werden in Koordinator-Werte übersetzt."""
    power = spec_for_key("Rated_Power")
    online = spec_for_key("online")
    assert power is not None
    assert online is not None
    assert format_state(800.0, power) == "800"
    assert format_state(True, online) == "on"
    assert format_state("offline", online) == "off"
    assert format_state(None, power) is None
    assert format_state({"nested": 1}, power) is None


def test_device_info_enthält_identifikator():
    """Geräte müssen über die Knoten-ID zuordenbar sein."""
    info = device_info("inv 1", "TSUN", "TSUN Gen3")
    assert ("tsun", "inv_1") in info["identifiers"]
    assert info["manufacturer"] == "TSUN"


def test_plattformen_sind_vollständig():
    """Alle für HACS relevanten Plattformen müssen Specs haben."""
    platforms = {spec.platform for spec in ENTITY_SPECS}
    assert {"sensor", "binary_sensor", "number", "select", "update"} <= platforms

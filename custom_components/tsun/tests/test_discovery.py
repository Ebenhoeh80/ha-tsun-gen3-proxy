"""Tests für die Knotenerkennung ohne Home-Assistant-Laufzeit."""

from custom_components.tsun.const import PROXY_NODE
from custom_components.tsun.parser import (
    ENTITY_SPECS,
    discovered_nodes,
    specs_for_node,
)


def test_ohne_daten_keine_knoten():
    """Ein leerer Eintrag erzeugt keine Platzhalter-Entitäten."""
    assert discovered_nodes(None) == set()
    assert discovered_nodes({}) == set()


def test_knoten_aus_mqtt_daten():
    """Veröffentlichte Knoten werden automatisch übernommen."""
    data = {"inv_1": {"rated_power": "120"}, "inv_2": {}}
    assert discovered_nodes(data) == {"inv_1", "inv_2"}


def test_legacy_knoten_bleibt_erhalten():
    """Bestehende Einträge mit einer echten Knoten-ID behalten ihren Knoten."""
    assert discovered_nodes({}, "inv_1") == {"inv_1"}
    assert discovered_nodes({"inv_2": {}}, "inv_1") == {"inv_1", "inv_2"}


def test_alter_standardwert_wird_ignoriert():
    """Der Platzhalter `inverter` erzeugt kein Phantom-Gerät."""
    assert discovered_nodes({}, "inverter") == set()
    assert discovered_nodes({"inv_1": {}}, "inverter") == {"inv_1"}


def test_leerer_legacy_knoten_wird_ignoriert():
    """Ein leerer gespeicherter Wert erzeugt keinen Platzhalter."""
    assert discovered_nodes({"inv_1": {}}, "") == {"inv_1"}


def test_proxy_nur_diagnose_sensoren():
    """Der Proxy-Knoten bekommt keine Wechselrichter-Summen oder Steuerung."""
    specs = [spec for spec in ENTITY_SPECS if spec.platform == "sensor"]
    proxy_suffixes = {spec.suffix for spec in specs_for_node(specs, PROXY_NODE)}
    assert "sw_exception" in proxy_suffixes
    assert "at_command_blocked" in proxy_suffixes
    assert "mqtt_published" in proxy_suffixes
    assert "rated_power" not in proxy_suffixes
    assert "total_generation_today" not in proxy_suffixes


def test_wechselrichter_bekommt_alle_spezifikationen():
    """Für echte Knoten bleibt die Entitätsauswahl unverändert."""
    specs = [spec for spec in ENTITY_SPECS if spec.platform == "sensor"]
    assert specs_for_node(specs, "inv_1") == specs

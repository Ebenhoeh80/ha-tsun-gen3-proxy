"""Tests für die Knotenerkennung ohne Home-Assistant-Laufzeit."""

from custom_components.tsun.parser import discovered_nodes


def test_ohne_daten_keine_knoten():
    """Ein leerer Eintrag erzeugt keine Platzhalter-Entitäten."""
    assert discovered_nodes(None) == set()
    assert discovered_nodes({}) == set()


def test_knoten_aus_mqtt_daten():
    """Veröffentlichte Knoten werden automatisch übernommen."""
    data = {"inv_1": {"rated_power": "120"}, "inv_2": {}}
    assert discovered_nodes(data) == {"inv_1", "inv_2"}


def test_legacy_knoten_bleibt_erhalten():
    """Bestehende Einträge mit node_id behalten ihren Knoten."""
    assert discovered_nodes({}, "inverter") == {"inverter"}
    assert discovered_nodes({"inv_1": {}}, "inverter") == {"inv_1", "inverter"}


def test_leerer_legacy_knoten_wird_ignoriert():
    """Ein leerer gespeicherter Wert erzeugt keinen Platzhalter."""
    assert discovered_nodes({"inv_1": {}}, "") == {"inv_1"}

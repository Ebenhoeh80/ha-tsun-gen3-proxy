"""Prüft, dass das Manifest von Home Assistant und HACS akzeptiert werden kann."""

import json
from pathlib import Path

_MANIFEST = Path(__file__).resolve().parents[1] / "manifest.json"
_ALLOWED_KEYS = {
    "domain",
    "name",
    "codeowners",
    "config_flow",
    "documentation",
    "integration_type",
    "iot_class",
    "issue_tracker",
    "version",
    "requirements",
    "dependencies",
    "after_dependencies",
    "keywords",
    "quality_scale",
    "loggers",
}


def test_manifest_enthält_nur_zulässige_schlüssel():
    """Ungültige Schlüssel lässt HA beim Laden der Integration weg."""
    data = json.loads(_MANIFEST.read_text(encoding="utf-8"))
    assert set(data) <= _ALLOWED_KEYS


def test_manifest_nutzt_ha_mqtt_integration():
    """Der MQTT-Client kommt aus Home Assistant, nicht aus pip."""
    data = json.loads(_MANIFEST.read_text(encoding="utf-8"))
    assert "mqtt" in data["dependencies"]
    assert data["requirements"] == []


def test_manifest_version_und_codeowners():
    """Version und Codeowner müssen gesetzt sein."""
    data = json.loads(_MANIFEST.read_text(encoding="utf-8"))
    assert data["version"].count(".") == 2
    assert data["codeowners"] and all(
        owner.startswith("@") for owner in data["codeowners"]
    )

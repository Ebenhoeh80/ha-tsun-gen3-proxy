"""Reine Hilfsfunktionen zum Verarbeiten der TSUN-MQTT-Nachrichten.

Dieses Modul hat bewusst keine Abhängigkeit von Home Assistant. Dadurch
lassen sich Topic-Auflösung, Payload-Auswertung und Entitätszuordnung
ohne HA-Laufzeit testen.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

from .const import (
    COMMAND_ACL_MODE,
    COMMAND_AT_RATE_LIMIT,
    ENTITY_CATEGORY_CONFIG,
    ENTITY_CATEGORY_DIAGNOSTIC,
    NUMBER_AT_RATE_LIMIT,
    SELECT_ACL_MODE,
    STATE_CLASS_MEASUREMENT,
    STATE_CLASS_TOTAL_INCREASING,
    TOPIC_PREFIX,
    UNIT_COUNT,
    UNIT_KILO_WATT_HOUR,
    UNIT_RATE,
    UNIT_WATT,
)


@dataclass(frozen=True)
class EntitySpec:
    """Beschreibung einer Entität, die aus Proxy-MQTT-Daten gespeist wird."""

    keys: tuple[str, ...]
    platform: str
    suffix: str
    name: str
    unit: str | None = None
    device_class: str | None = None
    state_class: str | None = None
    entity_category: str | None = None
    icon: str | None = None
    command: str | None = None
    options: tuple[str, ...] = ()
    min_value: float | None = None
    max_value: float | None = None
    # Leer = jede Topic-Gruppe. Eingeschränkte Gruppen verhindern, dass
    # verschachtelte PV-Werte die Wechselrichter-Summen überschreiben.
    groups: tuple[str, ...] = ()


ENTITY_SPECS: tuple[EntitySpec, ...] = (
    EntitySpec(
        ("Rated_Power", "rated_power"),
        "sensor",
        "rated_power",
        "Nennleistung",
        unit=UNIT_WATT,
        state_class=STATE_CLASS_MEASUREMENT,
        icon="mdi:solar-power",
        groups=("inverter",),
    ),
    EntitySpec(
        ("Daily_Generation", "total_generation_today"),
        "sensor",
        "total_generation_today",
        "Tageserzeugung",
        unit=UNIT_KILO_WATT_HOUR,
        device_class="energy",
        state_class=STATE_CLASS_TOTAL_INCREASING,
        icon="mdi:solar-power-variant",
        groups=("total",),
    ),
    EntitySpec(
        ("Total_Generation", "total_generation_total"),
        "sensor",
        "total_generation_total",
        "Gesamterzeugung",
        unit=UNIT_KILO_WATT_HOUR,
        device_class="energy",
        state_class=STATE_CLASS_TOTAL_INCREASING,
        icon="mdi:solar-power",
        groups=("total",),
    ),
    EntitySpec(
        ("SW_Exception", "sw_exception"),
        "sensor",
        "sw_exception",
        "Softwarefehler",
        unit=UNIT_COUNT,
        state_class=STATE_CLASS_MEASUREMENT,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        icon="mdi:counter",
        groups=("proxy",),
    ),
    EntitySpec(
        ("AT_Command_Blocked", "at_command_blocked"),
        "sensor",
        "at_command_blocked",
        "Blockierte AT-Befehle",
        unit=UNIT_COUNT,
        state_class=STATE_CLASS_MEASUREMENT,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        icon="mdi:alert",
        groups=("proxy",),
    ),
    EntitySpec(
        ("mqtt_published",),
        "sensor",
        "mqtt_published",
        "MQTT-Nachrichten gesendet",
        unit=UNIT_COUNT,
        state_class=STATE_CLASS_MEASUREMENT,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        icon="mdi:mqtt",
    ),
    EntitySpec(
        ("mqtt_received",),
        "sensor",
        "mqtt_received",
        "MQTT-Nachrichten empfangen",
        unit=UNIT_COUNT,
        state_class=STATE_CLASS_MEASUREMENT,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        icon="mdi:mqtt",
    ),
    EntitySpec(
        ("online",),
        "binary_sensor",
        "online",
        "Online",
        device_class="connectivity",
    ),
    EntitySpec(
        (),
        "number",
        NUMBER_AT_RATE_LIMIT,
        "AT-Befehlsrate",
        unit=UNIT_RATE,
        entity_category=ENTITY_CATEGORY_CONFIG,
        command=COMMAND_AT_RATE_LIMIT,
        min_value=0.0,
        max_value=100.0,
    ),
    EntitySpec(
        (),
        "select",
        SELECT_ACL_MODE,
        "AT-Zugriffsmodus",
        entity_category=ENTITY_CATEGORY_CONFIG,
        command=COMMAND_ACL_MODE,
        options=("standard", "strict", "disabled"),
    ),
    EntitySpec(
        (),
        "update",
        "update",
        "Update",
        icon="mdi:update",
    ),
)

_SPEC_BY_KEY: dict[str, EntitySpec] = {
    key: spec for spec in ENTITY_SPECS for key in spec.keys
}

_INVALID_ENTITY_CHARS = re.compile(r"[^a-z0-9_]+")


def sanitize(value: str) -> str:
    """Wandelt einen Namen in einen HA-Entitätsschlüssel um."""
    return _INVALID_ENTITY_CHARS.sub("_", value.strip().lower()).strip("_")


def parse_topic(topic: str, prefix: str = TOPIC_PREFIX) -> tuple[str, str] | None:
    """Liefert ``(node_id, gruppe)`` für einen Proxy-Topic zurück.

    Sowohl ``tsun/<node>/<gruppe>`` als auch das ältere Format
    ``tsun//<node>//<gruppe>`` werden akzeptiert.
    """
    parts = [part for part in topic.split("/") if part]
    if len(parts) < 3 or parts[0] != prefix:
        return None
    return parts[1], "/".join(parts[2:])


def _flatten(value: Any, target: dict[str, Any]) -> None:
    """Legt verschachtelte JSON-Objekte flach auf oberste Schlüssel."""
    if not isinstance(value, dict):
        return
    for key, item in value.items():
        if isinstance(item, dict):
            _flatten(item, target)
        else:
            target[str(key)] = item


def extract_values(payload: bytes | bytearray | str) -> dict[str, Any]:
    """Wandelt eine MQTT-Nachricht in flache Messwerte um.

    Der Proxy sendet JSON-Objekte, teils verschachtelt (z. B.
    ``{"pv1": {"Daily_Generation": 1.2}}``). Reine Zahlen landen unter
    ``value``. Welche Werte übernommen werden, entscheidet ``spec_for_key``
    anhand der Topic-Gruppe.
    """
    if isinstance(payload, (bytes, bytearray)):
        text = payload.decode("utf-8", errors="replace")
    else:
        text = payload

    text = text.strip()
    if not text:
        return {}

    try:
        decoded = json.loads(text)
    except (ValueError, TypeError):
        return {"value": text}

    if isinstance(decoded, dict):
        values: dict[str, Any] = {}
        _flatten(decoded, values)
        return values
    return {"value": decoded}


def spec_for_key(key: str, group: str | None = None) -> EntitySpec | None:
    """Findet die Entitätsdefinition zu einem Messwert-Schlüssel.

    Ist ``group`` angegeben, werden nur Entitäten akzeptiert, die für diese
    Topic-Gruppe vorgesehen sind. So können ``pv1.Daily_Generation`` und
    ``total.Daily_Generation`` nicht dieselbe Entität überschreiben.
    """
    spec = _SPEC_BY_KEY.get(key)
    if spec is None:
        return None
    if group is not None and spec.groups and group not in spec.groups:
        return None
    return spec


def unique_id(entry_id: str, node_id: str, spec: EntitySpec) -> str:
    """Baut eine stabile eindeutige ID für eine Entität."""
    return sanitize(f"{entry_id}_{node_id}_{spec.suffix}")


def device_info(node_id: str, manufacturer: str, model: str) -> dict[str, Any]:
    """Liefert die Geräteinformation für Home Assistant."""
    return {
        "identifiers": {(TOPIC_PREFIX, sanitize(node_id))},
        "manufacturer": manufacturer,
        "model": model,
        "name": f"TSUN {node_id}",
    }


def format_state(value: Any, spec: EntitySpec) -> str | None:
    """Normalisiert einen Messwert auf einen Zustand im Koordinator."""
    if value is None or isinstance(value, (dict, list)):
        return None
    if spec.platform == "binary_sensor":
        if isinstance(value, bool):
            return "on" if value else "off"
        text = str(value).strip().lower()
        if text in {"1", "true", "online", "on", "yes"}:
            return "on"
        if text in {"0", "false", "offline", "off", "no"}:
            return "off"
        return None
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, (int, float)):
        return f"{value:g}"
    text = str(value).strip()
    return text or None

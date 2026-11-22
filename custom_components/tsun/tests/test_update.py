"""Tests für die Update-Entität und den Versions-Fallback."""

from __future__ import annotations

import asyncio
from typing import Any

from custom_components.tsun.const import CONF_LATEST_VERSION, PROXY_NODE, VERSION
from custom_components.tsun.update import async_setup_entry


class _Entry:
    """Minimaler Config-Entry-Ersatz."""

    entry_id = "entry1"

    def __init__(self, data: dict[str, Any], options: dict[str, Any] | None = None) -> None:
        self.data = data
        self.options = options or {}

    def async_on_unload(self, func):
        """Stub: Aufräumen wird im Test nicht benötigt."""
        return func


class _Coordinator:
    """Minimaler Koordinator-Ersatz mit konfigurierbaren erkannten Knoten."""

    def __init__(self, nodes: tuple[str, ...] = ("inv_1",)) -> None:
        self.data: dict[str, dict[str, Any]] = {node: {} for node in nodes}

    def async_add_listener(self, callback):
        """Stub: kein Listener-Aufruf im Test."""
        return lambda: None


class _Hass:
    """Minimaler Home-Assistant-Ersatz."""

    def __init__(self, nodes: tuple[str, ...] = ("inv_1",)) -> None:
        self.data = {"tsun": {"entry1": _Coordinator(nodes)}}


def _entities(
    data: dict[str, Any],
    options: dict[str, Any] | None = None,
    nodes: tuple[str, ...] = ("inv_1",),
) -> list[Any]:
    """Erzeugt die Update-Entitäten mit den gegebenen MQTT-Knoten."""
    entities: list[Any] = []
    asyncio.run(
        async_setup_entry(
            _Hass(nodes),  # type: ignore[arg-type]
            _Entry(data, options),  # type: ignore[arg-type]
            lambda items: entities.extend(items),  # type: ignore[arg-type]
        )
    )
    return entities


def _latest(data: dict[str, Any], options: dict[str, Any] | None = None) -> tuple[str, str]:
    """Erzeugt die Update-Entität und liefert installierte/verfügbare Version."""
    entities = _entities(data, options)
    assert len(entities) == 1
    entity = entities[0]
    return entity._attr_installed_version, entity._attr_latest_version


def test_latest_version_aus_entry_data() -> None:
    """Ein gespeicherter Wert in `entry.data` hat Vorrang."""
    installed, latest = _latest(
        {CONF_LATEST_VERSION: "1.2.3"}, {CONF_LATEST_VERSION: "9.9.9"}
    )
    assert installed == VERSION
    assert latest == "1.2.3"


def test_latest_version_aus_optionen() -> None:
    """Ohne `entry.data` werden die Optionen herangezogen."""
    installed, latest = _latest({}, {CONF_LATEST_VERSION: "2.3.4"})
    assert installed == VERSION
    assert latest == "2.3.4"


def test_latest_version_fallback() -> None:
    """Ohne gespeicherte Version gilt die Code-Version."""
    installed, latest = _latest({}, {})
    assert installed == VERSION
    assert latest == VERSION


def test_nur_proxy_erzeugt_keine_update_entitaet() -> None:
    """Der Pseudoknoten `proxy` ist kein Wechselrichter mit Integrationsversion."""
    assert _entities({}, nodes=(PROXY_NODE,)) == []


def test_update_unique_id_ist_unabhaengig_vom_knoten() -> None:
    """Die Unique-ID bleibt stabil, auch wenn ein anderer Knoten liefert."""
    first = _entities({}, nodes=("inv_1",))
    second = _entities({}, nodes=("inv_2",))
    assert len(first) == len(second) == 1
    assert first[0]._attr_unique_id == second[0]._attr_unique_id
    assert "inv_1" not in first[0]._attr_unique_id
    assert "inv_2" not in second[0]._attr_unique_id

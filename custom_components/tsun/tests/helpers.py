"""Gemeinsame, gezielte Test-Hilfen (keine globalen HA-Stubs)."""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

from custom_components.tsun.coordinator import TsunCoordinator


def make_entry(
    entry_id: str = "entry1",
    data: dict[str, Any] | None = None,
    options: dict[str, Any] | None = None,
    runtime_data: Any = None,
) -> MagicMock:
    """Baut einen Config-Entry-Ersatz mit den vom Code genutzten Feldern."""
    entry = MagicMock()
    entry.entry_id = entry_id
    entry.data = data or {}
    entry.options = options or {}
    entry.runtime_data = runtime_data
    entry.unique_id = "tsun"
    entry.title = "TSUN Inverter"
    entry.async_on_unload = MagicMock()
    return entry


def make_coordinator(
    nodes: tuple[str, ...] = ("inv_1",), configured: str | None = None
) -> TsunCoordinator:
    """Baut einen Koordinator ohne HA-Loop, aber mit echtem Datenpfad.

    ``async_set_updated_data`` wird ersetzt, damit die reine Nachrichten-
    verarbeitung ohne Event-Loop testbar bleibt. Alle übrigen Methoden
    stammen aus der echten Klasse.
    """
    coordinator = object.__new__(TsunCoordinator)
    coordinator.data = {node: {} for node in nodes}
    coordinator.last_update_success = True
    coordinator.entry_id = "entry1"
    coordinator.configured_node = configured
    coordinator._unsubscribe = None
    coordinator._last_seen = {}
    coordinator._last_seen_wall = {}
    coordinator.hass = MagicMock()

    def _set_data(data: dict[str, Any]) -> None:
        coordinator.data = data

    setattr(  # noqa: B010 - gezielter Methodenersatz im Testzweck
        coordinator, "async_set_updated_data", MagicMock(side_effect=_set_data)
    )
    setattr(  # noqa: B010 - gezielter Methodenersatz im Testzweck
        coordinator, "async_add_listener", MagicMock(return_value=lambda: None)
    )
    return coordinator


def spec(suffix: str) -> Any:
    """Liefert die Entitätsdefinition zu einem Suffix."""
    from custom_components.tsun.parser import ENTITY_SPECS

    return next(item for item in ENTITY_SPECS if item.suffix == suffix)

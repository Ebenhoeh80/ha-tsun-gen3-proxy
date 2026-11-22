"""Tests für die Update-Entität und den Versions-Fallback."""

from __future__ import annotations

import asyncio
from typing import Any

from custom_components.tsun.const import CONF_LATEST_VERSION, VERSION
from custom_components.tsun.update import async_setup_entry


class _Entry:
    """Minimaler Config-Entry-Ersatz."""

    entry_id = "entry1"

    def __init__(self, data: dict[str, Any], options: dict[str, Any] | None = None) -> None:
        self.data = data
        self.options = options or {}


class _Hass:
    """Minimaler Home-Assistant-Ersatz."""

    def __init__(self) -> None:
        self.data = {"tsun": {"entry1": object()}}


def _latest(data: dict[str, Any], options: dict[str, Any] | None = None) -> tuple[str, str]:
    """Erzeugt die Update-Entität und liefert installierte/verfügbare Version."""
    entities: list[Any] = []
    asyncio.run(
        async_setup_entry(
            _Hass(),  # type: ignore[arg-type]
            _Entry(data, options),  # type: ignore[arg-type]
            lambda items: entities.extend(items),  # type: ignore[arg-type]
        )
    )
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

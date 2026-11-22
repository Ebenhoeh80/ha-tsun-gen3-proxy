"""Tests für die wiederhergestellten Konfigurations-Entitäten.

Die reinen Logiktests prüfen, dass gesetzte Werte einen HA-Neustart
überstehen und dass unplausible gespeicherte Werte verworfen werden.
"""

from __future__ import annotations

import asyncio
from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock, patch

from custom_components.tsun.number import TsunNumber
from custom_components.tsun.parser import ENTITY_SPECS
from custom_components.tsun.select import TsunSelect


def _spec(suffix: str):
    """Liefert die Entitätsdefinition zu einem Suffix."""
    return next(spec for spec in ENTITY_SPECS if spec.suffix == suffix)


def test_number_wert_wird_wiederhergestellt() -> None:
    """Ein gespeicherter AT-Wert im gültigen Bereich wird übernommen."""
    coordinator: Any = object()
    entity = TsunNumber(coordinator, "entry1", "inv1", _spec("at_rate_limit"), 0.0)
    last = SimpleNamespace(native_value=42.0)
    with patch.object(
        entity, "async_get_last_number_data", new=AsyncMock(return_value=last)
    ):
        asyncio.run(entity.async_added_to_hass())
    assert entity.native_value == 42.0


def test_number_ungueltiger_wert_wird_verworfen() -> None:
    """Ein Wert außerhalb erlaubter Grenzen bleibt unberücksichtigt."""
    coordinator: Any = object()
    entity = TsunNumber(coordinator, "entry1", "inv1", _spec("at_rate_limit"), 5.0)
    last = SimpleNamespace(native_value=999.0)
    with patch.object(
        entity, "async_get_last_number_data", new=AsyncMock(return_value=last)
    ):
        asyncio.run(entity.async_added_to_hass())
    assert entity.native_value == 5.0


def test_select_auswahl_wird_wiederhergestellt() -> None:
    """Eine gespeicherte, gültige Auswahl wird übernommen."""
    coordinator: Any = object()
    entity = TsunSelect(coordinator, "entry1", "inv1", _spec("acl_mode"), "standard")
    last = SimpleNamespace(state="strict")
    with patch.object(
        entity, "async_get_last_state", new=AsyncMock(return_value=last)
    ):
        asyncio.run(entity.async_added_to_hass())
    assert entity.current_option == "strict"


def test_select_unbekannte_auswahl_wird_verworfen() -> None:
    """Ein nicht mehr angebotener Wert fällt auf den Standard zurück."""
    coordinator: Any = object()
    entity = TsunSelect(coordinator, "entry1", "inv1", _spec("acl_mode"), "standard")
    last = SimpleNamespace(state="veraltet")
    with patch.object(
        entity, "async_get_last_state", new=AsyncMock(return_value=last)
    ):
        asyncio.run(entity.async_added_to_hass())
    assert entity.current_option == "standard"

"""Tests für die Update-Entität und den Versions-Fallback."""

from __future__ import annotations

import asyncio
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

from homeassistant.components.update import UpdateDeviceClass

from custom_components.tsun.const import CONF_LATEST_VERSION, PROXY_NODE, VERSION
from custom_components.tsun.tests.helpers import make_coordinator, make_entry
from custom_components.tsun.update import (
    ReleaseInfo,
    async_fetch_release,
    async_setup_entry,
)


def _entities(
    data: dict[str, Any] | None = None,
    options: dict[str, Any] | None = None,
    nodes: tuple[str, ...] = ("inv_1",),
) -> list[Any]:
    """Erzeugt die Update-Entitäten mit den gegebenen MQTT-Knoten."""
    coordinator = make_coordinator(nodes=nodes)
    entry = make_entry(data=data, options=options, runtime_data=coordinator)
    entities: list[Any] = []
    asyncio.run(
        async_setup_entry(
            coordinator.hass,
            entry,
            lambda items: entities.extend(items),  # type: ignore[arg-type]
        )
    )
    return entities


def test_latest_version_nur_aus_altem_entry_data() -> None:
    """Ein veralteter Wert in `entry.data` bleibt als Offline-Fallback."""
    entities = _entities(data={CONF_LATEST_VERSION: "1.2.3"}, options={})
    assert len(entities) == 1
    assert entities[0]._attr_latest_version == "1.2.3"


def test_optionen_schalten_release_check_nicht_ab() -> None:
    """Ein Wert in den Optionen darf die GitHub-Abfrage nicht deaktivieren."""
    entities = _entities(data={}, options={CONF_LATEST_VERSION: "9.9.9"})
    assert entities[0]._attr_latest_version == VERSION


def test_latest_version_fallback() -> None:
    """Ohne gespeicherte Version gilt die Code-Version."""
    entities = _entities(data={}, options={})
    assert entities[0]._attr_latest_version == VERSION


def test_nur_proxy_erzeugt_keine_update_entitaet() -> None:
    """Der Pseudoknoten `proxy` ist kein Wechselrichter mit Integrationsversion."""
    assert _entities(nodes=(PROXY_NODE,)) == []


def test_update_unique_id_ist_unabhaengig_vom_knoten() -> None:
    """Die Unique-ID bleibt stabil, auch wenn ein anderer Knoten liefert."""
    first = _entities(nodes=("inv_1",))
    second = _entities(nodes=("inv_2",))
    assert first[0]._attr_unique_id == second[0]._attr_unique_id
    assert "inv_1" not in first[0]._attr_unique_id
    assert "inv_2" not in second[0]._attr_unique_id


def test_update_ist_firmware_update() -> None:
    """Die Device-Class erlaubt HA, die Entität als Firmware-Update zu zeigen."""
    assert _entities()[0]._attr_device_class is UpdateDeviceClass.FIRMWARE


def test_github_release_wird_uebernommen() -> None:
    """Die Update-Entität zeigt die vom GitHub-Release gemeldete Version."""
    entity = _entities()[0]
    info = ReleaseInfo(
        tag="9.9.9",
        url="https://github.com/example/release",
        summary="Neue Funktionen",
    )
    with (
        patch(
            "custom_components.tsun.update.async_fetch_release",
            new=AsyncMock(return_value=info),
        ),
        patch.object(entity, "async_write_ha_state"),
        patch(
            "custom_components.tsun.update.async_track_time_interval",
            return_value=lambda: None,
        ),
    ):
        asyncio.run(entity.async_added_to_hass())
    assert entity._attr_latest_version == "9.9.9"
    assert entity._attr_release_url == "https://github.com/example/release"
    assert entity._attr_release_summary == "Neue Funktionen"


def test_manual_version_verhindert_github_abfrage() -> None:
    """Ein manuell gesetzter Wert bleibt maßgeblich und spart die Abfrage."""
    entity = _entities(data={CONF_LATEST_VERSION: "1.2.3"})[0]
    with (
        patch(
            "custom_components.tsun.update.async_fetch_release",
            new=AsyncMock(),
        ) as fetch,
        patch.object(entity, "async_write_ha_state"),
        patch(
            "custom_components.tsun.update.async_track_time_interval",
            return_value=lambda: None,
        ),
    ):
        asyncio.run(entity.async_added_to_hass())
    fetch.assert_not_awaited()
    assert entity._attr_latest_version == "1.2.3"


def test_fetch_release_ohne_session_kein_fehler() -> None:
    """Ohne HTTP-Session bleibt die letzte bekannte Version stehen."""
    hass = MagicMock()
    with patch(
        "custom_components.tsun.update.async_get_clientsession", return_value=None
    ):
        assert asyncio.run(async_fetch_release(hass)) is None

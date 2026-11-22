"""Update-Plattform für die TSUN-Inverter-Integration.

Die neueste Version wird über die GitHub-Releases-API ermittelt (HA-Best-
Practice für Update-Entitäten). Ein veralteter, manuell gesetzter Wert aus
einem Config Entry der Version 0.2.x bleibt als Offline-Fallback erhalten.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import timedelta

import aiohttp
from homeassistant.components.update import UpdateDeviceClass, UpdateEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_time_interval

from . import TsunConfigEntry
from .const import CONF_LATEST_VERSION, DEFAULT_VERSION, PROXY_NODE, VERSION
from .coordinator import TsunCoordinator
from .entity import TsunEntity
from .parser import ENTITY_SPECS, EntitySpec, discovered_nodes, sanitize

_PARALLEL_UPDATES = 0
_REPO = "Ebenhoeh80/ha-tsun-inverter"
_RELEASES_URL = f"https://api.github.com/repos/{_REPO}/releases/latest"
_RELEASE_PAGE = f"https://github.com/{_REPO}/releases"
_REFRESH_INTERVAL = timedelta(hours=6)
_REQUEST_TIMEOUT = aiohttp.ClientTimeout(total=10)
_FALLBACK_SUMMARY = "Release-Hinweise auf GitHub"


@dataclass(frozen=True)
class ReleaseInfo:
    """Veröffentlichte Version und zugehörige Release-Seite."""

    tag: str
    url: str
    summary: str


async def async_fetch_release(hass: HomeAssistant) -> ReleaseInfo | None:
    """Fragt das neueste GitHub-Release ab; bei Fehlern ``None``.

    Die Abfrage ist bewusst fehlertolerant: Update-Entitäten dürfen den
    Start einer Integration nicht verzögern oder abbrechen. Ohne Netzwerk
    bleibt die zuletzt bekannte Version stehen.
    """
    session = async_get_clientsession(hass)
    if session is None:  # defensiv: ohne Session bleibt die Version stehen
        return None
    try:
        async with session.get(_RELEASES_URL, timeout=_REQUEST_TIMEOUT) as response:
            response.raise_for_status()
            payload = await response.json()
    except aiohttp.ClientError, TimeoutError, ValueError:
        return None

    if not isinstance(payload, dict):
        return None
    tag = str(payload.get("tag_name") or "").strip().lstrip("v")
    if not tag:
        return None
    return ReleaseInfo(
        tag=tag,
        url=str(payload.get("html_url") or _RELEASE_PAGE),
        summary=str(payload.get("body") or _FALLBACK_SUMMARY).strip()[:255]
        or _FALLBACK_SUMMARY,
    )


async def async_setup_entry(
    hass: HomeAssistant,
    entry: TsunConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Erzeugt eine Update-Entität, sobald ein Wechselrichter bekannt ist."""
    coordinator: TsunCoordinator = entry.runtime_data
    specs = [spec for spec in ENTITY_SPECS if spec.platform == "update"]
    if not specs:
        return

    configured = coordinator.configured_node
    known_node: str | None = None

    def _add_new() -> None:
        nonlocal known_node
        if known_node is not None:
            return
        # Der Pseudoknoten `proxy` enthält nur Diagnosewerte des Proxys,
        # keine Integrationsversion. Er darf die Entität nicht anlegen.
        nodes = discovered_nodes(coordinator.data, configured) - {PROXY_NODE}
        if not nodes:
            return
        known_node = configured if configured in nodes else min(nodes)
        # A-02: der Options-Flow schreibt `latest_version` nicht mehr. Nur
        # noch ein Wert aus einem alten Config Entry wird als Fallback
        # berücksichtigt; danach ist die GitHub-Abfrage wieder aktiv.
        manual = str(entry.data.get(CONF_LATEST_VERSION) or "")
        async_add_entities(
            [TsunUpdate(coordinator, entry.entry_id, known_node, specs[0], manual)]
        )

    _add_new()
    entry.async_on_unload(coordinator.async_add_listener(_add_new))


class TsunUpdate(TsunEntity, UpdateEntity):
    """Zeigt installierte und verfügbare Version der Integration."""

    def __init__(
        self,
        coordinator: TsunCoordinator,
        entry_id: str,
        node_id: str,
        spec: EntitySpec,
        manual_version: str,
    ) -> None:
        """Initialisiert die Update-Entität mit stabiler ID ohne Knotenbezug."""
        super().__init__(coordinator, entry_id, node_id, spec)
        # Die Version gehört zur Integration, nicht zu einem Wechselrichter.
        # Ohne den Knoten in der Unique-ID bleibt die Entität beim Neustart
        # stabil, auch wenn ein anderer Knoten zuerst Daten liefert.
        self._attr_unique_id = f"{sanitize(entry_id)}_{spec.suffix}"
        self._attr_device_class = UpdateDeviceClass.FIRMWARE
        self._manual_version = manual_version
        self._attr_installed_version = VERSION
        self._attr_latest_version = manual_version or DEFAULT_VERSION
        self._attr_release_url = _RELEASE_PAGE
        self._attr_release_summary = _FALLBACK_SUMMARY
        self._cancel_refresh: Callable[[], None] | None = None

    @property
    def available(self) -> bool:
        """Die Integrationsversion gilt unabhängig vom Zustand eines Knotens.

        Die Entität wird aus Stabilitätsgründen einem Gerät zugeordnet, darf
        aber nicht `unavailable` werden, wenn genau dieser Knoten verschwindet
        (A-22).
        """
        return self.coordinator.last_update_success

    async def async_added_to_hass(self) -> None:
        """Lädt die Release-Info und plant die nächste Abfrage ein."""
        await super().async_added_to_hass()
        await self._async_refresh_release()
        self._cancel_refresh = async_track_time_interval(
            self.hass, self._async_refresh_release, _REFRESH_INTERVAL
        )

    async def async_will_remove_from_hass(self) -> None:
        """Beendet die periodische Abfrage beim Entfernen der Entität."""
        if self._cancel_refresh is not None:
            self._cancel_refresh()
            self._cancel_refresh = None
        await super().async_will_remove_from_hass()

    async def _async_refresh_release(self, _now: object = None) -> None:
        """Aktualisiert Version und Release-Text von GitHub.

        Ein manuell gesetzter Wert hat Vorrang und verhindert die Abfrage,
        damit die Entität auch ohne Internet eine stabile Anzeige behält.
        """
        if self._manual_version:
            return
        release = await async_fetch_release(self.hass)
        if release is not None:
            self._attr_latest_version = release.tag
            self._attr_release_url = release.url
            self._attr_release_summary = release.summary
        self.async_write_ha_state()

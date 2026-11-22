"""Update-Plattform für die TSUN-Inverter-Integration."""

from __future__ import annotations

from homeassistant.components.update import UpdateEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_LATEST_VERSION, CONF_NODE_ID, DEFAULT_VERSION, DOMAIN, VERSION
from .coordinator import TsunCoordinator
from .entity import TsunEntity
from .parser import ENTITY_SPECS, EntitySpec, discovered_nodes

_PLATFORM = "update"


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Erzeugt eine Update-Entität, sobald ein Knoten bekannt ist."""
    coordinator: TsunCoordinator = hass.data[DOMAIN][entry.entry_id]
    specs = [spec for spec in ENTITY_SPECS if spec.platform == _PLATFORM]
    if not specs:
        return

    configured = entry.data.get(CONF_NODE_ID)
    known_node: str | None = None

    def _add_new() -> None:
        nonlocal known_node
        if known_node is not None:
            return
        nodes = discovered_nodes(coordinator.data, configured)
        if not nodes:
            return
        known_node = configured if configured in nodes else min(nodes)
        latest = str(
            entry.data.get(CONF_LATEST_VERSION)
            or entry.options.get(CONF_LATEST_VERSION)
            or VERSION
        )
        async_add_entities(
            [
                TsunUpdate(
                    coordinator, entry.entry_id, known_node, specs[0], latest
                )
            ]
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
        latest: str,
    ) -> None:
        """Initialisiert die Update-Entität."""
        super().__init__(coordinator, entry_id, node_id, spec)
        self._attr_installed_version = VERSION
        self._attr_latest_version = latest or DEFAULT_VERSION
        self._attr_release_summary = "Release-Hinweise auf GitHub"

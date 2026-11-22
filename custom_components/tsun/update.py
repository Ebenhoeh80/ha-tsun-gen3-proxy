"""Update-Plattform für die TSUN-Inverter-Integration."""

from __future__ import annotations

from homeassistant.components.update import UpdateEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_LATEST_VERSION,
    CONF_NODE_ID,
    DEFAULT_NODE_ID,
    DEFAULT_VERSION,
    DOMAIN,
    VERSION,
)
from .coordinator import TsunCoordinator
from .entity import TsunEntity
from .parser import ENTITY_SPECS, EntitySpec

_PLATFORM = "update"


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Erzeugt die Update-Entität für den bekannten Release-Stand."""
    coordinator: TsunCoordinator = hass.data[DOMAIN][entry.entry_id]
    node_id = entry.data.get(CONF_NODE_ID, DEFAULT_NODE_ID)
    specs = [spec for spec in ENTITY_SPECS if spec.platform == _PLATFORM]

    if specs:
        async_add_entities(
            [
                TsunUpdate(
                    coordinator,
                    entry.entry_id,
                    node_id,
                    specs[0],
                    str(entry.options.get(CONF_LATEST_VERSION, VERSION)),
                )
            ]
        )


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

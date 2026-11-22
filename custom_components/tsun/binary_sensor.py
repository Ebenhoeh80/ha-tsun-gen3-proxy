"""Binärsensor-Plattform für die TSUN-Inverter-Integration."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_NODE_ID, DOMAIN
from .coordinator import TsunCoordinator
from .entity import TsunEntity
from .parser import ENTITY_SPECS, EntitySpec, discovered_nodes

_PLATFORM = "binary_sensor"


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Erzeugt Binärsensoren für alle bekannten Knoten."""
    coordinator: TsunCoordinator = hass.data[DOMAIN][entry.entry_id]
    specs = [spec for spec in ENTITY_SPECS if spec.platform == _PLATFORM]
    known: set[str] = set()

    def _add_new() -> None:
        nodes = discovered_nodes(coordinator.data, entry.data.get(CONF_NODE_ID))
        new_nodes = nodes - known
        if not new_nodes:
            return
        known.update(new_nodes)
        async_add_entities(
            [
                TsunBinarySensor(coordinator, entry.entry_id, node, spec)
                for node in sorted(new_nodes)
                for spec in specs
            ]
        )

    _add_new()
    entry.async_on_unload(coordinator.async_add_listener(_add_new))


class TsunBinarySensor(TsunEntity, BinarySensorEntity):
    """Binärzustand eines Knotens."""

    def __init__(
        self,
        coordinator: TsunCoordinator,
        entry_id: str,
        node_id: str,
        spec: EntitySpec,
    ) -> None:
        """Initialisiert den Binärsensor."""
        super().__init__(coordinator, entry_id, node_id, spec)
        if spec.device_class:
            self._attr_device_class = BinarySensorDeviceClass(spec.device_class)

    @property
    def is_on(self) -> bool | None:
        """Liefert den aktuellen Zustand."""
        value = (self.coordinator.data or {}).get(self.node_id, {}).get(
            self.spec.suffix
        )
        if value is None:
            return None
        return str(value) == "on"

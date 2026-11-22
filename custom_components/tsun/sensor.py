"""Sensor-Plattform für die TSUN-Inverter-Integration."""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_NODE_ID, DOMAIN
from .coordinator import TsunCoordinator
from .entity import TsunEntity
from .parser import ENTITY_SPECS, EntitySpec, discovered_nodes, specs_for_node

_PLATFORM = "sensor"


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Erzeugt Sensoren für alle bekannten Knoten."""
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
                TsunSensor(coordinator, entry.entry_id, node, spec)
                for node in sorted(new_nodes)
                for spec in specs_for_node(specs, node)
            ]
        )

    _add_new()
    entry.async_on_unload(coordinator.async_add_listener(_add_new))


class TsunSensor(TsunEntity, SensorEntity):
    """Sensor mit einem Messwert aus dem Koordinator."""

    def __init__(
        self,
        coordinator: TsunCoordinator,
        entry_id: str,
        node_id: str,
        spec: EntitySpec,
    ) -> None:
        """Initialisiert den Sensor."""
        super().__init__(coordinator, entry_id, node_id, spec)
        if spec.unit:
            self._attr_native_unit_of_measurement = spec.unit
        if spec.device_class:
            self._attr_device_class = SensorDeviceClass(spec.device_class)
        if spec.state_class:
            self._attr_state_class = SensorStateClass(spec.state_class)
        if spec.entity_category:
            self._attr_entity_category = EntityCategory(spec.entity_category)
        if spec.icon:
            self._attr_icon = spec.icon

    @property
    def native_value(self) -> str | None:
        """Liefert den neuesten Messwert."""
        return (self.coordinator.data or {}).get(self.node_id, {}).get(
            self.spec.suffix
        )

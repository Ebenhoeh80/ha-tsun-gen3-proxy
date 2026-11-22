"""Sensor-Plattform für die TSUN-Inverter-Integration."""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import TsunConfigEntry
from .coordinator import TsunCoordinator
from .entity import TsunEntity
from .parser import ENTITY_SPECS, EntitySpec, specs_for_node

_PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: TsunConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Erzeugt Sensoren für alle bekannten Knoten."""
    coordinator: TsunCoordinator = entry.runtime_data
    specs = [spec for spec in ENTITY_SPECS if spec.platform == "sensor"]
    known: set[str] = set()

    def _add_new() -> None:
        new_nodes = coordinator.new_nodes(known)
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

    @property
    def native_value(self) -> str | int | float | None:
        """Liefert den neuesten Messwert als nativen Typ."""
        return (self.coordinator.data or {}).get(self.node_id, {}).get(self.spec.suffix)

"""Gemeinsame Basisklasse für TSUN-Entitäten."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, MODEL
from .coordinator import TsunCoordinator
from .parser import EntitySpec, unique_id


class TsunEntity(CoordinatorEntity[TsunCoordinator]):
    """Basisklasse mit Gerätezuordnung und Verfügbarkeitsprüfung."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: TsunCoordinator,
        entry_id: str,
        node_id: str,
        spec: EntitySpec,
    ) -> None:
        """Verknüpft die Entität mit Knoten, Koordinator und Gerät."""
        super().__init__(coordinator)
        self.node_id = node_id
        self.spec = spec
        self._attr_unique_id = unique_id(entry_id, node_id, spec)
        self._attr_name = spec.name
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, node_id)},
            manufacturer=MANUFACTURER,
            model=MODEL,
            name=f"TSUN {node_id}",
        )

    @property
    def available(self) -> bool:
        """Die Entität ist verfügbar, sobald der Knoten Daten liefert."""
        return bool(self.coordinator.data and self.node_id in self.coordinator.data)

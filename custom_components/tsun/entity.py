"""Gemeinsame Basisklasse für TSUN-Entitäten."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, MODEL
from .coordinator import TsunCoordinator
from .parser import EntitySpec, sanitize, unique_id


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
        # Name und Icon kommen aus strings.json/translations und icons.json.
        # Die Unique-ID bleibt unverändert, daher gibt es keine
        # Registry-Migration (A-16, A-32).
        self._attr_translation_key = spec.suffix
        device_info = DeviceInfo(
            identifiers={(DOMAIN, sanitize(node_id))},
            manufacturer=MANUFACTURER,
            model=MODEL,
            name=f"TSUN {node_id}",
        )
        # Im Standard-Setup ist die Knoten-ID die Seriennummer des Wechsel-
        # richters. Nur rein numerische IDs werden daher als Seriennummer
        # übernommen; Platzhalter wie `inv_1` bleiben unangetastet (A-15).
        if node_id.isdigit():
            device_info["serial_number"] = node_id
        self._attr_device_info = device_info

    @property
    def available(self) -> bool:
        """Verfügbar nur bei erfolgreichem Coordinator und frischem Knoten.

        Ohne Last-Seen-Prüfung bleiben Entitäten nach einem Proxy-/Broker-
        Ausfall dauerhaft ``available`` und zeigen veraltete Werte (A-21).
        """
        return super().available and not self.coordinator.is_stale(self.node_id)

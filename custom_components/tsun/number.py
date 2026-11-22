"""Number-Plattform für die TSUN-Inverter-Integration."""

from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_NODE_ID,
    DEFAULT_AT_RATE_LIMIT,
    DEFAULT_NODE_ID,
    DOMAIN,
)
from .coordinator import TsunCoordinator
from .entity import TsunEntity
from .parser import ENTITY_SPECS, EntitySpec

_PLATFORM = "number"


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Erzeugt die konfigurierbaren Zahlen-Entitäten."""
    coordinator: TsunCoordinator = hass.data[DOMAIN][entry.entry_id]
    node_id = entry.data.get(CONF_NODE_ID, DEFAULT_NODE_ID)
    specs = [spec for spec in ENTITY_SPECS if spec.platform == _PLATFORM]

    entities: list[TsunNumber] = []
    for spec in specs:
        initial = float(
            entry.options.get(spec.suffix, DEFAULT_AT_RATE_LIMIT)
            if spec.suffix == "at_rate_limit"
            else entry.options.get(spec.suffix, spec.min_value or 0)
        )
        entities.append(
            TsunNumber(coordinator, entry.entry_id, node_id, spec, initial)
        )

    if entities:
        async_add_entities(entities)


class TsunNumber(TsunEntity, NumberEntity):
    """Zahlenwert, der per MQTT an den Proxy gesendet wird."""

    def __init__(
        self,
        coordinator: TsunCoordinator,
        entry_id: str,
        node_id: str,
        spec: EntitySpec,
        initial: float,
    ) -> None:
        """Initialisiert die Zahlen-Entität."""
        super().__init__(coordinator, entry_id, node_id, spec)
        self._value = initial
        self._attr_mode = NumberMode.BOX
        self._attr_entity_category = EntityCategory.CONFIG
        if spec.unit:
            self._attr_native_unit_of_measurement = spec.unit
        if spec.min_value is not None:
            self._attr_native_min_value = spec.min_value
        if spec.max_value is not None:
            self._attr_native_max_value = spec.max_value
        if spec.icon:
            self._attr_icon = spec.icon

    @property
    def native_value(self) -> float:
        """Liefert den aktuell gesetzten Wert."""
        return self._value

    async def async_set_native_value(self, value: float) -> None:
        """Sendet einen neuen Wert an den Proxy."""
        if self.spec.command is None:
            return
        await self.coordinator.async_send_command(
            self.node_id, self.spec.command, f"{value:g}"
        )
        self._value = value
        self.async_write_ha_state()

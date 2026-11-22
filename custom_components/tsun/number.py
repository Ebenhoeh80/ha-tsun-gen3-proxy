"""Number-Plattform für die TSUN-Inverter-Integration."""

from __future__ import annotations

from homeassistant.components.number import NumberMode, RestoreNumber
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import TsunConfigEntry
from .const import DEFAULT_AT_RATE_LIMIT
from .coordinator import TsunCoordinator
from .entity import TsunEntity
from .parser import ENTITY_SPECS, EntitySpec

_PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant,
    entry: TsunConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Erzeugt konfigurierbare Zahlen-Entitäten für alle erkannten Knoten."""
    coordinator: TsunCoordinator = entry.runtime_data
    specs = [spec for spec in ENTITY_SPECS if spec.platform == "number"]
    known: set[str] = set()

    def _initial(spec: EntitySpec) -> float:
        fallback = (
            DEFAULT_AT_RATE_LIMIT
            if spec.suffix == "at_rate_limit"
            else spec.min_value or 0
        )
        return float(entry.options.get(spec.suffix, fallback))

    def _add_new() -> None:
        new_nodes = coordinator.new_nodes(known, exclude_proxy=True)
        if not new_nodes:
            return
        known.update(new_nodes)
        async_add_entities(
            [
                TsunNumber(coordinator, entry.entry_id, node, spec, _initial(spec))
                for node in sorted(new_nodes)
                for spec in specs
            ]
        )

    _add_new()
    entry.async_on_unload(coordinator.async_add_listener(_add_new))


class TsunNumber(TsunEntity, RestoreNumber):
    """Zahlenwert, der per MQTT an den Proxy gesendet wird.

    Als ``RestoreNumber`` übersteht der gesetzte Wert einen HA-Neustart.
    Ohne Wiederherstellung fiel die AT-Befehlsrate sonst auf den Standard
    zurück, obwohl der Proxy den alten Wert noch verwendet.
    """

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

    async def async_added_to_hass(self) -> None:
        """Stellt den zuletzt gesetzten Wert nach einem Neustart wieder her."""
        await super().async_added_to_hass()
        last = await self.async_get_last_number_data()
        if last is None or last.native_value is None:
            return
        value = float(last.native_value)
        if self.native_min_value <= value <= self.native_max_value:
            self._value = value

    @property
    def native_value(self) -> float:
        """Liefert den aktuell gesetzten Wert."""
        return self._value

    async def async_set_native_value(self, value: float) -> None:
        """Sendet einen neuen Wert an den Proxy."""
        if self.spec.command is None:
            return
        sent = await self.coordinator.async_send_command(
            self.node_id, self.spec.command, f"{value:g}"
        )
        if not sent:
            return
        self._value = value
        self.async_write_ha_state()

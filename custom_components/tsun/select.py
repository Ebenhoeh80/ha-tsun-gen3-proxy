"""Select-Plattform für die TSUN-Inverter-Integration."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_NODE_ID, DOMAIN
from .coordinator import TsunCoordinator
from .entity import TsunEntity
from .parser import ENTITY_SPECS, EntitySpec, discovered_nodes

_PLATFORM = "select"


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Erzeugt Auswahl-Entitäten für alle erkannten Knoten."""
    coordinator: TsunCoordinator = hass.data[DOMAIN][entry.entry_id]
    specs = [spec for spec in ENTITY_SPECS if spec.platform == _PLATFORM]
    known: set[str] = set()

    def _initial(spec: EntitySpec) -> str:
        fallback = spec.options[0] if spec.options else ""
        return str(entry.options.get(spec.suffix, fallback))

    def _add_new() -> None:
        nodes = discovered_nodes(coordinator.data, entry.data.get(CONF_NODE_ID))
        new_nodes = nodes - known
        if not new_nodes:
            return
        known.update(new_nodes)
        async_add_entities(
            [
                TsunSelect(coordinator, entry.entry_id, node, spec, _initial(spec))
                for node in sorted(new_nodes)
                for spec in specs
            ]
        )

    _add_new()
    entry.async_on_unload(coordinator.async_add_listener(_add_new))


class TsunSelect(TsunEntity, SelectEntity):
    """Auswahlwert, der per MQTT an den Proxy gesendet wird."""

    def __init__(
        self,
        coordinator: TsunCoordinator,
        entry_id: str,
        node_id: str,
        spec: EntitySpec,
        initial: str,
    ) -> None:
        """Initialisiert die Auswahl-Entität."""
        super().__init__(coordinator, entry_id, node_id, spec)
        self._value = initial
        self._attr_entity_category = EntityCategory.CONFIG
        self._attr_options = list(spec.options)
        if spec.icon:
            self._attr_icon = spec.icon

    @property
    def current_option(self) -> str | None:
        """Liefert die aktuelle Auswahl."""
        return self._value

    async def async_select_option(self, option: str) -> None:
        """Sendet die neue Auswahl an den Proxy."""
        if self.spec.command is None:
            return
        await self.coordinator.async_send_command(
            self.node_id, self.spec.command, option
        )
        self._value = option
        self.async_write_ha_state()

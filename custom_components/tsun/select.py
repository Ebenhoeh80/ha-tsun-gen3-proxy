"""Select-Plattform für die TSUN-Inverter-Integration."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from . import TsunConfigEntry
from .coordinator import TsunCoordinator
from .entity import TsunEntity
from .parser import ENTITY_SPECS, EntitySpec

_PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant,
    entry: TsunConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Erzeugt Auswahl-Entitäten für alle erkannten Knoten."""
    coordinator: TsunCoordinator = entry.runtime_data
    specs = [spec for spec in ENTITY_SPECS if spec.platform == "select"]
    known: set[str] = set()

    def _initial(spec: EntitySpec) -> str:
        fallback = spec.options[0] if spec.options else ""
        return str(entry.options.get(spec.suffix, fallback))

    def _add_new() -> None:
        new_nodes = coordinator.new_nodes(known, exclude_proxy=True)
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


class TsunSelect(TsunEntity, SelectEntity, RestoreEntity):
    """Auswahlwert, der per MQTT an den Proxy gesendet wird.

    Als ``RestoreEntity`` bleibt die getroffene Auswahl auch nach einem
    HA-Neustart erhalten und muss nicht erneut gesetzt werden.
    """

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

    async def async_added_to_hass(self) -> None:
        """Stellt die zuletzt gültige Auswahl nach einem Neustart wieder her."""
        await super().async_added_to_hass()
        last = await self.async_get_last_state()
        if last is not None and last.state in self.options:
            self._value = last.state

    @property
    def current_option(self) -> str | None:
        """Liefert die aktuelle Auswahl."""
        return self._value

    async def async_select_option(self, option: str) -> None:
        """Sendet die neue Auswahl an den Proxy."""
        if self.spec.command is None:
            return
        sent = await self.coordinator.async_send_command(
            self.node_id, self.spec.command, option
        )
        if not sent:
            return
        self._value = option
        self.async_write_ha_state()

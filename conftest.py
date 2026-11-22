"""Minimale Stubs, damit die reinen Logiktests ohne HA-Installation laufen.

Die echte Integration benötigt Home Assistant. Für die hier geprüften
Hilfsfunktionen reichen diese Platzhalter aus. Ein vollständiger
HA-Testlauf benötigt `pytest-homeassistant-custom-component`.
"""

from __future__ import annotations

import sys
import types
from types import SimpleNamespace


def _package(name: str) -> types.ModuleType:
    module = sys.modules.get(name)
    if module is None:
        module = types.ModuleType(name)
        module.__path__ = []  # type: ignore[attr-defined]
        sys.modules[name] = module
    return module


def _module(name: str, **attributes) -> types.ModuleType:
    module = sys.modules.get(name)
    if module is None:
        module = types.ModuleType(name)
        sys.modules[name] = module
    for key, value in attributes.items():
        setattr(module, key, value)
    return module


class _Base:
    """Stub-Basisklasse mit Generics-Unterstützung."""

    def __init__(self, *args, **kwargs) -> None:
        """Stub: Konstruktorargumente verwerfen (bewusster Kompromiß).

        Damit werden falsche Signaturen gegenüber der echten HA-API nicht
        erkannt; dafür bleiben die Tests ohne installiertes Home Assistant
        lauffähig. Attribute wie ``coordinator`` werden hier nicht gesetzt.
        """

    def __init_subclass__(cls, **kwargs) -> None:
        """Erlaubt Klassenargumente wie ``domain=...``."""
        super().__init_subclass__()

    def __class_getitem__(cls, item):
        """Erlaubt ``CoordinatorEntity[T]``."""
        return cls

    def async_write_ha_state(self) -> None:
        """Stub."""

    async def async_added_to_hass(self) -> None:
        """Stub: Restore-Entitäten rufen dies beim Hinzufügen auf."""
        if not hasattr(self, "hass"):
            self.hass = None

    async def async_will_remove_from_hass(self) -> None:
        """Stub: Entitäten rufen dies beim Entfernen auf."""

    async def async_get_last_number_data(self):
        """Stub: kein gespeicherter Zahlenwert in der Testumgebung."""
        return

    async def async_get_last_state(self):
        """Stub: kein gespeicherter Zustand in der Testumgebung."""
        return


class _NumberEntity(_Base):
    """Stub mit den Properties, die RestoreNumber beim Wiederherstellen liest."""

    @property
    def native_min_value(self) -> float:
        return getattr(self, "_attr_native_min_value", 0.0)

    @property
    def native_max_value(self) -> float:
        return getattr(self, "_attr_native_max_value", 100.0)


class _SelectEntity(_Base):
    """Stub mit der Options-Property, die RestoreSelect prüft."""

    @property
    def options(self) -> list[str]:
        return list(getattr(self, "_attr_options", []))


class _ConfigFlow(_Base):
    pass


class _OptionsFlow(_Base):
    pass


class _Coordinator(_Base):
    def __init__(self, hass, logger, **kwargs) -> None:
        self.hass = hass
        self.data: dict = {}

    async def async_config_entry_first_refresh(self) -> None:
        """Stub."""

    def async_set_updated_data(self, data) -> None:
        self.data = data

    def async_add_listener(self, callback):
        """Stub."""
        return lambda: None


async def _async_subscribe(hass, topic, callback, **kwargs):
    """Stub für mqtt.async_subscribe."""
    return lambda: None


async def _async_publish(hass, topic, payload, **kwargs) -> None:
    """Stub für mqtt.async_publish."""


async def _async_wait_for_mqtt_client(hass) -> bool:
    """Stub: MQTT-Client in der Testumgebung als verfügbar annehmen."""
    return True


class _ConfigEntryNotReady(Exception):
    """Stub für das HA-Retry-Signal beim Setup."""


def _identity(value):
    """Stub für Enum-Konstruktoren."""
    return value


ha = _package("homeassistant")
_module("homeassistant.core", HomeAssistant=_Base, callback=lambda fn: fn)
config_entries = _module(
    "homeassistant.config_entries",
    ConfigEntry=_Base,
    ConfigFlow=_ConfigFlow,
    ConfigFlowResult=dict,
    OptionsFlow=_OptionsFlow,
)
_module("homeassistant.data_entry_flow", FlowResult=dict)
_module("homeassistant.const", EntityCategory=object)
_module("homeassistant.exceptions", ConfigEntryNotReady=_ConfigEntryNotReady)

components = _package("homeassistant.components")
_module(
    "homeassistant.components.mqtt",
    async_subscribe=_async_subscribe,
    async_publish=_async_publish,
    async_wait_for_mqtt_client=_async_wait_for_mqtt_client,
)
_module(
    "homeassistant.components.sensor",
    SensorEntity=_Base,
    SensorDeviceClass=_identity,
    SensorStateClass=_identity,
)
_module(
    "homeassistant.components.binary_sensor",
    BinarySensorEntity=_Base,
    BinarySensorDeviceClass=_identity,
)
_module(
    "homeassistant.components.number",
    NumberEntity=_NumberEntity,
    NumberMode=SimpleNamespace(BOX="box"),
    RestoreNumber=_NumberEntity,
)
_module("homeassistant.components.select", SelectEntity=_SelectEntity)
_module("homeassistant.components.update", UpdateEntity=_Base)

helpers = _package("homeassistant.helpers")
_module(
    "homeassistant.helpers.entity",
    EntityCategory=SimpleNamespace(CONFIG="config", DIAGNOSTIC="diagnostic"),
)
_module("homeassistant.helpers.entity_platform", AddEntitiesCallback=object)
_module("homeassistant.helpers.device_registry", DeviceInfo=lambda **kwargs: kwargs)
_module("homeassistant.helpers.selector", selector=lambda schema: schema)
_module("homeassistant.helpers.restore_state", RestoreEntity=_Base)
_module(
    "homeassistant.helpers.aiohttp_client",
    async_get_clientsession=lambda hass: None,
)
_module(
    "homeassistant.helpers.event",
    async_track_time_interval=lambda hass, action, interval: (lambda: None),
)
_module(
    "homeassistant.helpers.update_coordinator",
    DataUpdateCoordinator=_Coordinator,
    CoordinatorEntity=_Base,
)
_module(
    "aiohttp",
    ClientError=type("ClientError", (Exception,), {}),
    ClientTimeout=type(
        "ClientTimeout", (), {"__init__": lambda self, **kwargs: None}
    ),
)
_module(
    "aiomqtt",
    Client=type("Client", (), {"__init__": lambda self, **kwargs: None}),
)
_module(
    "voluptuous",
    Schema=type("Schema", (), {"__init__": lambda self, schema: None}),
    Optional=lambda key, default=None: key,
    Required=lambda key, default=None: key,
    All=lambda *args: None,
    Range=lambda min=None, max=None: None,
)

ha.core = sys.modules["homeassistant.core"]
ha.config_entries = config_entries
ha.components = components
ha.helpers = helpers

"""Konfigurationsablauf für die TSUN-Inverter-Integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.components.mqtt import async_wait_for_mqtt_client
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.core import callback

from .const import (
    CONF_AT_RATE_LIMIT,
    CONF_LATEST_VERSION,
    DEFAULT_AT_RATE_LIMIT,
    DEFAULT_VERSION,
    DOMAIN,
    NAME,
)


class TsunConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):  # type: ignore[call-arg]
    """Behandelt den Konfigurationsablauf."""

    VERSION = 1
    MINOR_VERSION = 2

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Bestätigt die Einrichtung über die vorhandene HA-MQTT-Integration."""
        if self._async_current_entries():
            return self.async_abort(reason="already_configured")

        if user_input is not None:
            await self.async_set_unique_id(DOMAIN)
            self._abort_if_unique_id_configured()
            # Ein leeres Formular bietet keine Möglichkeit, MQTT nachträglich
            # einzurichten. Ohne Client wäre das Setup nur ein generischer
            # Fehler -> klarer Abbruch mit Handlungsanweisung (vgl. HA-Core).
            if not await async_wait_for_mqtt_client(self.hass):
                return self.async_abort(reason="mqtt_unavailable")
            return self.async_create_entry(title=NAME, data={})

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({}),
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        """Liefert den Options-Ablauf."""
        return TsunOptionsFlow(config_entry)


class TsunOptionsFlow(config_entries.OptionsFlow):
    """Optionen zur Laufzeit ändern."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Speichert den Konfigurationseintrag."""
        self._entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Zeigt und speichert die Optionen."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current = self._entry.options
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_AT_RATE_LIMIT,
                        default=current.get(CONF_AT_RATE_LIMIT, DEFAULT_AT_RATE_LIMIT),
                    ): vol.All(int, vol.Range(min=0, max=100)),
                    vol.Optional(
                        CONF_LATEST_VERSION,
                        default=current.get(CONF_LATEST_VERSION, DEFAULT_VERSION),
                    ): str,
                }
            ),
        )

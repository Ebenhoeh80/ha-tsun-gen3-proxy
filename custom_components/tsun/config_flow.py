"""Konfigurationsablauf für die TSUN-Gen3-Proxy-Integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.core import callback
from homeassistant.helpers.selector import selector

from .const import (
    CONF_AT_RATE_LIMIT,
    CONF_LATEST_VERSION,
    CONF_MQTT_HOST,
    CONF_MQTT_PASSWORD,
    CONF_MQTT_PORT,
    CONF_MQTT_USER,
    CONF_NODE_ID,
    DEFAULT_HOST,
    DEFAULT_NODE_ID,
    DEFAULT_PORT,
    DEFAULT_VERSION,
    DOMAIN,
)


class TsunConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):  # type: ignore[call-arg]
    """Behandelt den Konfigurationsablauf."""

    VERSION = 1
    MINOR_VERSION = 2

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Fragt die MQTT-Verbindung ab."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                port = int(user_input.get(CONF_MQTT_PORT, DEFAULT_PORT))
                if not 1 <= port <= 65535:
                    raise ValueError("Ungültiger Port")
            except (TypeError, ValueError):
                errors[CONF_MQTT_PORT] = "invalid_port"
            else:
                user_input[CONF_MQTT_PORT] = port
                await self.async_set_unique_id(
                    f"{user_input.get(CONF_MQTT_HOST, DEFAULT_HOST)}:{port}"
                )
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=user_input.get("title", DOMAIN), data=user_input
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_MQTT_HOST, default=DEFAULT_HOST): str,
                    vol.Required(CONF_MQTT_PORT, default=DEFAULT_PORT): int,
                    vol.Optional(CONF_MQTT_USER): str,
                    vol.Optional(CONF_MQTT_PASSWORD): selector(
                        {"text": {"type": "password"}}
                    ),
                    vol.Optional("title", default=DOMAIN): str,
                    vol.Optional(CONF_NODE_ID, default=DEFAULT_NODE_ID): str,
                    vol.Optional(CONF_LATEST_VERSION, default=DEFAULT_VERSION): str,
                }
            ),
            errors=errors,
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
                        default=current.get(CONF_AT_RATE_LIMIT, 0),
                    ): vol.All(int, vol.Range(min=0, max=100)),
                    vol.Optional(
                        CONF_LATEST_VERSION,
                        default=current.get(CONF_LATEST_VERSION, DEFAULT_VERSION),
                    ): str,
                }
            ),
        )

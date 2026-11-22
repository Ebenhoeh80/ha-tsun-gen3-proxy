"""Tests für die gruppenabhängige Zuordnung der MQTT-Messwerte."""

from __future__ import annotations

import asyncio
from typing import Any
from unittest.mock import AsyncMock, patch

from homeassistant.exceptions import ConfigEntryNotReady

from custom_components.tsun.coordinator import TsunCoordinator


class _Entry:
    """Minimaler Config-Entry-Ersatz."""

    entry_id = "entry1"


class _Message:
    """Minimaler MQTT-Message-Ersatz."""

    def __init__(self, topic: str, payload: str) -> None:
        self.topic = topic
        self.payload = payload


def _coordinator() -> TsunCoordinator:
    return TsunCoordinator(object(), _Entry())  # type: ignore[arg-type]


def _message(topic: str, payload: str) -> Any:
    return _Message(topic, payload)


def test_pv_eingaenge_ueberschreiben_wechselrichter_summen_nicht() -> None:
    """Verschachtelte PV-Werte dürfen nicht als Gesamterzeugung landen."""
    coordinator = _coordinator()

    coordinator._handle_message(
        _message(
            "tsun/inv1/input",
            '{"pv1":{"Daily_Generation":1.2},"pv2":{"Daily_Generation":0.4}}',
        )
    )
    assert coordinator.data == {}

    coordinator._handle_message(
        _message(
            "tsun/inv1/total",
            '{"Daily_Generation":7.5,"Total_Generation":123.4}',
        )
    )
    values = coordinator.data["inv1"]
    assert values["total_generation_today"] == "7.5"
    assert values["total_generation_total"] == "123.4"


def test_gruppen_sind_fuer_ihre_schluessel_zustaendig() -> None:
    """Nennleistung und Proxy-Zähler kommen aus ihren eigenen Gruppen."""
    coordinator = _coordinator()

    coordinator._handle_message(
        _message("tsun/inv1/input", '{"Rated_Power":800}')
    )
    assert coordinator.data == {}

    coordinator._handle_message(
        _message("tsun/inv1/inverter", '{"Rated_Power":800}')
    )
    coordinator._handle_message(
        _message("tsun/proxy/proxy", '{"SW_Exception":2,"AT_Command_Blocked":1}')
    )

    inverter = coordinator.data["inv1"]
    proxy = coordinator.data["proxy"]
    assert inverter["rated_power"] == "800"
    assert proxy["sw_exception"] == "2"
    assert proxy["at_command_blocked"] == "1"


def test_alte_topic_formats_funktionieren_weiter() -> None:
    """Das Legacy-Format tsun//node//gruppe bleibt akzeptiert."""
    coordinator = _coordinator()
    coordinator._handle_message(
        _message("tsun//inv 1//total", '{"Daily_Generation":3.5}')
    )
    assert coordinator.data["inv 1"]["total_generation_today"] == "3.5"


def test_setup_wartet_auf_mqtt_client() -> None:
    """Ohne MQTT-Client wird der Setup-Versuch später wiederholt."""
    coordinator = _coordinator()
    with patch(
        "custom_components.tsun.coordinator.mqtt.async_wait_for_mqtt_client",
        new=AsyncMock(return_value=False),
    ):
        try:
            asyncio.run(coordinator.async_setup())
        except ConfigEntryNotReady:
            pass
        else:
            raise AssertionError("ConfigEntryNotReady erwartet")
    assert coordinator._unsubscribe is None


def test_setup_abonniert_erst_nach_mqtt_client() -> None:
    """Das Abonnement startet erst, wenn der Client verfügbar ist."""
    coordinator = _coordinator()
    unsubscribe = lambda: None
    with (
        patch(
            "custom_components.tsun.coordinator.mqtt.async_wait_for_mqtt_client",
            new=AsyncMock(return_value=True),
        ),
        patch(
            "custom_components.tsun.coordinator.mqtt.async_subscribe",
            new=AsyncMock(return_value=unsubscribe),
        ) as subscribe,
    ):
        asyncio.run(coordinator.async_setup())
    subscribe.assert_awaited_once()
    assert coordinator._unsubscribe is unsubscribe


def test_befehl_wird_nicht_retainiert() -> None:
    """Steuer-Kommandos dürfen nicht im Broker hängen bleiben."""
    coordinator = _coordinator()
    with patch(
        "custom_components.tsun.coordinator.mqtt.async_publish",
        new=AsyncMock(),
    ) as publish:
        asyncio.run(
            coordinator.async_send_command("inv1", "set_at_rate_limit", "30")
        )
    publish.assert_awaited_once()
    assert publish.await_args is not None
    assert publish.await_args.args[1] == "tsun/inv1/set_at_rate_limit"
    assert publish.await_args.kwargs["retain"] is False

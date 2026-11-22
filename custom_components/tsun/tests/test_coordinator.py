"""Tests für Verarbeitung, Verfügbarkeit und Grenzen des Koordinators."""

from __future__ import annotations

import asyncio
import time
from typing import Any
from unittest.mock import AsyncMock, patch

from homeassistant.exceptions import ConfigEntryNotReady

from custom_components.tsun.tests.helpers import make_coordinator


class _Message:
    """Minimaler MQTT-Message-Ersatz."""

    def __init__(self, topic: str, payload: str) -> None:
        self.topic = topic
        self.payload = payload


def _message(topic: str, payload: str) -> Any:
    return _Message(topic, payload)


def test_pv_eingaenge_ueberschreiben_wechselrichter_summen_nicht() -> None:
    """Verschachtelte PV-Werte dürfen nicht als Gesamterzeugung landen."""
    coordinator = make_coordinator(nodes=())
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
    assert values["total_generation_today"] == 7.5
    assert values["total_generation_total"] == 123.4
    assert isinstance(values["total_generation_today"], float)


def test_gruppen_sind_fuer_ihre_schluessel_zustaendig() -> None:
    """Nennleistung und Proxy-Zähler kommen aus ihren eigenen Gruppen."""
    coordinator = make_coordinator(nodes=())
    coordinator._handle_message(_message("tsun/inv1/input", '{"Rated_Power":800}'))
    assert coordinator.data == {}

    coordinator._handle_message(_message("tsun/inv1/inverter", '{"Rated_Power":800}'))
    coordinator._handle_message(
        _message("tsun/proxy/proxy", '{"SW_Exception":2,"AT_Command_Blocked":1}')
    )

    inverter = coordinator.data["inv1"]
    proxy = coordinator.data["proxy"]
    assert inverter["rated_power"] == 800
    assert proxy["sw_exception"] == 2
    assert proxy["at_command_blocked"] == 1


def test_alte_topic_formats_funktionieren_weiter() -> None:
    """Das Legacy-Format tsun//node//gruppe bleibt akzeptiert."""
    coordinator = make_coordinator(nodes=())
    coordinator._handle_message(
        _message("tsun//inv 1//total", '{"Daily_Generation":3.5}')
    )
    assert coordinator.data["inv 1"]["total_generation_today"] == 3.5


def test_setup_wartet_auf_mqtt_client() -> None:
    """Ohne MQTT-Client wird der Setup-Versuch später wiederholt."""
    coordinator = make_coordinator()
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
    coordinator = make_coordinator()

    def unsubscribe() -> None:
        return None

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
    coordinator = make_coordinator()
    with patch(
        "custom_components.tsun.coordinator.mqtt.async_publish",
        new=AsyncMock(),
    ) as publish:
        sent = asyncio.run(
            coordinator.async_send_command("inv1", "set_at_rate_limit", "30")
        )
    assert sent is True
    publish.assert_awaited_once()
    assert publish.await_args is not None
    assert publish.await_args.args[1] == "tsun/inv1/set_at_rate_limit"
    assert publish.await_args.kwargs["retain"] is False


def test_publish_fehler_wird_gemeldet() -> None:
    """Ein Publish-Fehler darf nicht als Erfolg an die UI gemeldet werden."""
    from homeassistant.exceptions import HomeAssistantError

    coordinator = make_coordinator()
    with patch(
        "custom_components.tsun.coordinator.mqtt.async_publish",
        new=AsyncMock(side_effect=HomeAssistantError("broker weg")),
    ):
        sent = asyncio.run(
            coordinator.async_send_command("inv1", "set_acl_mode", "strict")
        )
    assert sent is False


def test_heartbeat_hält_knoten_frisch() -> None:
    """Auch Nachrichten ohne Messwerte gelten als Lebenszeichen."""
    coordinator = make_coordinator(nodes=())
    coordinator._handle_message(_message("tsun/inv1/proxy", "{}"))
    assert coordinator.last_seen("inv1") is not None
    assert coordinator.is_stale("inv1") is False


def test_veralteter_knoten_wird_erkannt() -> None:
    """Ohne Nachrichten wird ein Knoten nach dem Timeout als veraltet markiert."""
    coordinator = make_coordinator(nodes=("inv1",))
    coordinator._last_seen["inv1"] = time.monotonic() - 500
    assert coordinator.is_stale("inv1") is True


def test_knoten_obergrenze_greift() -> None:
    """Ein fremder Publisher kann nicht unbegrenzt Entitäten erzeugen."""
    coordinator = make_coordinator(nodes=())
    for index in range(20):
        coordinator._handle_message(
            _message(f"tsun/node{index:02d}/inverter", '{"Rated_Power":800}')
        )
    assert len(coordinator.data) <= 16


def test_konfigurierter_knoten_hat_vorrang() -> None:
    """Der explizit konfigurierte Knoten wird bei der Obergrenze bevorzugt."""
    coordinator = make_coordinator(nodes=(), configured="mein_wechselrichter")
    for index in range(20):
        coordinator._handle_message(
            _message(f"tsun/node{index:02d}/inverter", '{"Rated_Power":800}')
        )
    assert "mein_wechselrichter" in coordinator.new_nodes(set(), exclude_proxy=True)

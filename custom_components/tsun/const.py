"""Konstanten für die TSUN-Gen3-Proxy-Integration."""

from __future__ import annotations

DOMAIN = "tsun"
NAME = "TSUN-Gen3-Proxy"
MANUFACTURER = "TSUN"
MODEL = "TSUN-Gen3-Proxy"

PLATFORMS: tuple[str, ...] = (
    "sensor",
    "binary_sensor",
    "number",
    "select",
    "update",
)

# Konfiguration
CONF_MQTT_HOST = "mqtt_host"
CONF_MQTT_PORT = "mqtt_port"
CONF_MQTT_USER = "mqtt_user"
CONF_MQTT_PASSWORD = "mqtt_password"
CONF_NODE_ID = "node_id"
CONF_LATEST_VERSION = "latest_version"
CONF_AT_RATE_LIMIT = "at_rate_limit"

DEFAULT_HOST = "mqtt"
DEFAULT_PORT = 1883
DEFAULT_NODE_ID = "inverter"
DEFAULT_VERSION = "0.1.0"
DEFAULT_AT_RATE_LIMIT = 0

TOPIC_PREFIX = "tsun"
TOPIC_STATUS = "status"

# Messwerte (Schlüssel des Upstream-Proxys)
SENSOR_RATED_POWER = "rated_power"
SENSOR_TOTAL_GEN_TODAY = "total_generation_today"
SENSOR_TOTAL_GEN_TOTAL = "total_generation_total"
SENSOR_SW_EXCEPTION = "sw_exception"
SENSOR_AT_BLOCKED = "at_command_blocked"
SENSOR_MQTT_PUBLISHED = "mqtt_published"
SENSOR_MQTT_RECEIVED = "mqtt_received"
SENSOR_ONLINE = "online"

BINARY_SENSOR_ONLINE = "online"
NUMBER_AT_RATE_LIMIT = "at_rate_limit"
SELECT_ACL_MODE = "acl_mode"
UPDATE_ENTITY = "update"

# Befehle
COMMAND_AT_RATE_LIMIT = "set_at_rate_limit"
COMMAND_ACL_MODE = "set_acl_mode"

# Kategorien und Klassen
ENTITY_CATEGORY_DIAGNOSTIC = "diagnostic"
ENTITY_CATEGORY_CONFIG = "config"
STATE_CLASS_MEASUREMENT = "measurement"
STATE_CLASS_TOTAL_INCREASING = "total_increasing"

UNIT_WATT = "W"
UNIT_KILO_WATT_HOUR = "kWh"
UNIT_COUNT = "count"
UNIT_RATE = "cmd/min"

DEVICE_IDENTIFIERS = (DOMAIN, "proxy")
LOGGER = "custom_components.tsun"
VERSION = "0.1.0"

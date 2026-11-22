"""Konstanten für die TSUN-Inverter-Integration."""

from __future__ import annotations

DOMAIN = "tsun"
NAME = "TSUN Inverter"
MANUFACTURER = "TSUN"
MODEL = "TSUN Gen3"

PLATFORMS: tuple[str, ...] = (
    "sensor",
    "binary_sensor",
    "number",
    "select",
    "update",
)

# Konfiguration
CONF_MQTT_HOST = "mqtt_host"
CONF_MQTT_USER = "mqtt_user"
CONF_MQTT_PASSWORD = "mqtt_password"
CONF_NODE_ID = "node_id"
CONF_LATEST_VERSION = "latest_version"
CONF_AT_RATE_LIMIT = "at_rate_limit"

DEFAULT_NODE_ID = "inverter"
DEFAULT_AT_RATE_LIMIT = 0

TOPIC_PREFIX = "tsun"
PROXY_NODE = "proxy"

# Schutzgrenzen für die Wildcard-Subscription `tsun/#`. Der Proxy veröffentlicht
# üblicherweise einen Wechselrichter; die Obergrenze verhindert, dass ein
# fremder Publisher oder eine retainte Alt-Nachricht unbegrenzt Entitäten
# erzeugt. Bestehende Knoten werden nie entfernt (A-33).
MAX_NODES = 16
MAX_PAYLOAD_DEPTH = 8
# Upstream-Datenintervall 300 s, Heartbeat 120 s. 420 s lässt Toleranz für
# Nordpole/Kurzwelle, ohne einen echten Ausfall zu kaschieren (A-21).
STALE_TIMEOUT_SECONDS = 420

# Befehle. Für diese Topics ist keine bestätigte Upstream-Response belegt;
# die Entitäten bleiben aus Gründen der Rückwärtskompatibilität erhalten,
# sind aber in der README klar dokumentiert.
COMMAND_AT_RATE_LIMIT = "set_at_rate_limit"
COMMAND_ACL_MODE = "set_acl_mode"
NUMBER_AT_RATE_LIMIT = "at_rate_limit"
SELECT_ACL_MODE = "acl_mode"

# Kategorien und Klassen (Werte der HA-Enums, damit parser.py HA-frei bleibt)
ENTITY_CATEGORY_DIAGNOSTIC = "diagnostic"
ENTITY_CATEGORY_CONFIG = "config"
STATE_CLASS_MEASUREMENT = "measurement"
STATE_CLASS_TOTAL_INCREASING = "total_increasing"
DEVICE_CLASS_POWER = "power"
DEVICE_CLASS_ENERGY = "energy"
DEVICE_CLASS_CONNECTIVITY = "connectivity"

UNIT_WATT = "W"
UNIT_KILO_WATT_HOUR = "kWh"
UNIT_COUNT = "count"
UNIT_RATE = "cmd/min"

LOGGER = "custom_components.tsun"
VERSION = "0.3.0"
DEFAULT_VERSION = VERSION

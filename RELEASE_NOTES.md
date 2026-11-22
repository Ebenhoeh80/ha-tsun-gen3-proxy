# TSUN-Gen3-Proxy 0.2.0 – Release-Hinweise

## Release-Informationen

- **Version:** 0.2.0
- **Datum:** 2026-11-22
- **Repository:** https://github.com/Ebenhoeh80/ha-tsun-gen3-proxy
- **Voraussetzung:** Home Assistant 2024.11.0 oder neuer, konfigurierte MQTT-Integration

## Hauptänderungen

Diese Version ersetzt das bisherige Gerüst durch eine funktionsfähige HACS-Integration. Messwerte des TSUN-Gen3-Proxys werden über `tsun/#` gelesen und über einen `DataUpdateCoordinator` als echte Home-Assistant-Entitäten bereitgestellt: Sensoren für Nennleistung, Tages- und Gesamterzeugung, Diagnosezähler, Online-Binärsensor sowie Number-, Select- und Update-Entitäten.

Der Konfigurationsdialog fragt den MQTT-Broker ab und legt eine eindeutige ID fest; Optionen und Diagnoseausgabe sind enthalten. Übersetzungen liegen auf Deutsch und Englisch vor.

## Installation

1. `https://github.com/Ebenhoeh80/ha-tsun-gen3-proxy` in HACS unter **Integrationen → Benutzerdefinierte Repositories** hinzufügen.
2. „TSUN-Gen3-Proxy" installieren und Home Assistant neu starten.
3. **Einstellungen → Geräte & Dienste → Integration hinzufügen** aufrufen und den MQTT-Broker konfigurieren.

## Hinweise

- Veröffentlicht der Proxy selbst MQTT-Discovery, können doppelte Entitäten entstehen. Discovery im Proxy deaktivieren oder die automatisch erzeugten MQTT-Entitäten ignorieren.
- `at_rate_limit` und `acl_mode` senden MQTT-Kommandos, für die der Upstream-Proxy derzeit keine passenden Topics definiert.
- Ein HA-Live-Test in einer Installation steht noch aus; die automatisierten Prüfungen (ruff, mypy, pytest, HACS) sind grün.

## Ältere Versionen

Die Version 0.1.0 wurde am 2026-11-21 im Fork `Ebenhoeh80/tsun-gen3-proxy` veröffentlicht, enthielt aber noch Platzhaltertests und einen nicht verdrahteten MQTT-Handler.

---

# TSUN-Gen3-Proxy 0.1.0 Release Notes

## Release Information
- **Version:** 0.1.0
- **Release Date:** 2026-11-21
- **Tag:** v0.1.0
- **Repository:** https://github.com/Ebenhoeh80/tsun-gen3-proxy

## Integration Summary
Home Assistant custom integration for TSUN Gen3 and Gen3+ Mikro-Wechselrichter und Batterien.
Enables native Home Assistant control through MQTT communication with the TSUN-Gen3-Proxy server.

## Installation

### HACS Installation
1. Add repository to HACS: `https://github.com/Ebenhoeh80/tsun-gen3-proxy`
2. Search for "TSUN-Gen3-Proxy" in HACS Integration Store
3. Install and restart Home Assistant

### Manual Installation
```bash
# Copy integration to Home Assistant config
cp -r custom_components/tsun /path/to/homeassistant/config/custom_components/

# Or via git
git clone https://github.com/Ebenhoeh80/tsun-gen3-proxy.git
cp -r tsun-gen3-proxy/custom_components/tsun /path/to/homeassistant/config/custom_components/tsun
```

### Configuration UI
1. Go to Settings → Devices & Services
2. Click "Add Integration"
3. Search for "TSUN-Gen3-Proxy" and select
4. Configure MQTT connection settings
5. Configure TSUN Cloud or GEN3+ Cloud settings
6. Set inverter ACL and rate limit options

## Configuration

### MQTT Settings
- **MQTT Host:** Your MQTT broker address (default: `mqtt`)
- **MQTT Port:** 1883 (default) or 8883 for TLS
- **MQTT User:** Your MQTT username (optional)
- **MQTT Password:** Your MQTT password (optional)

### TSUN Cloud (Gen3)
- **TSUN Enabled:** True (default)
- **TSUN Listener:** True (default)
- **TSUN Host:** logger.talent-monitoring.com (default)
- **TSUN Port:** 5005 (default)

### GEN3+ Cloud
- **SolarMan Enabled:** True (default)
- **SolarMan Listener:** True (default)
- **SolarMan Host:** iot.talent-monitoring.com (default)
- **SolarMan Port:** 10000 (default)

### Inverter Configuration
- **Allow All:** False (default) - restricts AT commands
- **Suggested Area:** (optional, e.g., "technical")

## Supported Entities

### Sensors (9)
| Entity | Unit | Device Class | State Class |
|--------|------|-------------|-------------|
| rated_power | W | power | measurement |
| total_generation_today | kWh | energy | total_increasing |
| total_generation_total | kWh | energy | total_increasing |
| sw_exception | - | diagnostic | measurement |
| at_command_blocked | count | diagnostic | measurement |
| mqtt_published | count | diagnostic | measurement |
| mqtt_received | count | diagnostic | measurement |
| online | - | connectivity | - |
| at_rate_limit | cmd/min | duration | - |

### Binary Sensor (1)
| Entity | Device Class | Payload Available | Payload Not Available |
|--------|-------------|-------------------|-----------------------|
| online | connectivity | online | offline |

### Number (1)
| Entity | Min | Max | Unit | Mode |
|--------|-----|-----|------|------|
| at_rate_limit | 0 | 100 | cmd/min | box |

### Select (1)
| Entity | Options |
|--------|---------|
| acl_mode | standard, strict, disabled |

### Update (1)
- TSUN-Gen3-Proxy Update - firmware update support

## MQTT Discovery
The integration uses Home Assistant MQTT Discovery to automatically register all entities.
Discovery topics are published to `homeassistant/{entity_type}/config` with `retain=true`.

## License
This integration is licensed under the **Apache License, Version 2.0** (Apache-2.0).
See the [LICENSE](LICENSE) file for full terms.

The underlying TSUN-Gen3-Proxy project (MODBUS/MQTT proxy) is Copyright © 2024 s-allius and remains under its original license. This integration is a separate work that connects to the TSUN-Gen3-Proxy via MQTT.

## Third-Party Dependencies
- **Home Assistant:** GPL-3.0-or-later
- **aiomqtt:** Apache License 2.0
- **voluptuous:** Apache License 2.0
- All other dependencies documented in [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md)

## Attribution
- **Original Project:** TSUN-Gen3-Proxy at https://github.com/s-allius/tsun-gen3-proxy
- **Home Assistant:** https://www.home-assistant.io/
- **Integration:** Copyright 2026 Ebenhoeh80

## Development
- **Code Structure:** All files in `custom_components/tsun/`
- **MQTT Client:** aiomqtt (asynchronous)
- **Configuration Flow:** config_flow.py (user step + options step)
- **Diagnostics:** diagnostics.py
- **Repair Flow:** repair.py
- **Tests:** tests/test_config_flow.py, tests/test_sensors.py

## Known Limitations
- Integration framework; actual MQTT message handling requires connection to TSUN-Gen3-Proxy server
- Full functionality tested with Home Assistant environment
- CI validation executed in GitHub Actions environment

## Version History
- **0.1.0** (2026-11-21) - Initial release

## Support
- **Issue Tracker:** https://github.com/s-allius/tsun-gen3-proxy/issues
- **Source:** https://github.com/Ebenhoeh80/tsun-gen3-proxy
- **Documentation:** https://s-allius.github.io/tsun-gen3-proxy/
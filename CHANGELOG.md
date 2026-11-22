# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/lang/en/).

## [Unreleased]

### Changed

- Lizenz der Integration von Apache-2.0 auf MIT umgestellt (Nutzerentscheidung 2026-11-22); die Lizenz des Upstream-TSUN-Gen3-Proxys bleibt unverändert

## [0.2.1] - 2026-11-22

### Fixed

- PV-Werte aus `tsun/<knoten>/input` überschrieben die Wechselrichter-Summen aus `tsun/<knoten>/total`; Messwerte werden jetzt nach Topic-Gruppe zugeordnet
- `const.VERSION` und Manifest auf 0.2.1 angeglichen; Update-Entität berücksichtigt auch `entry.data`
- Nicht zulässiger Manifest-Schlüssel `keywords` entfernt; `hassfest` als zusätzlicher CI-Job

### Changed

- README und RELEASE_NOTES: Hinweis, dass MQTT-Host/-Port und Zugangsdaten nicht verwendet werden; veralteter 0.1.0-Block in den Release-Hinweisen auf eine historische Notiz reduziert

## [0.2.0] - 2026-11-22

### Added

- HACS-Repository `Ebenhoeh80/ha-tsun-inverter` mit `hacs.json`, CI und deutscher/englischer Übersetzung
- `DataUpdateCoordinator` mit Push-Updates über die Home-Assistant-MQTT-Integration (`tsun/#`)
- Reine Parserlogik für Topic-Formate, verschachtelte JSON-Payloads und Entitätszuordnung
- Echte Entitäts-Plattformen: Sensor, Binärsensor, Number, Select und Update; neue Knoten zur Laufzeit
- Konfigurationsdialog mit Unique-ID und Options-Ablauf, Diagnose mit Passwort-Redaktion
- 15 aussagekräftige Logiktests, Ruff- und MyPy-Prüfung, HACS-Validierung
- Mindestversion Home Assistant 2024.11.0 (`ConfigFlowResult`, Koordinator-Config-Entry)

### Changed

- Eigener MQTT-Client und State-Store-Manipulation durch HA-MQTT-Integration und echte Entitäten ersetzt
- Manifest auf HA-zulässige Schlüssel reduziert: `dependencies: ["mqtt"]`, `requirements: []`, `iot_class: local_push`
- Alte Platzhaltermodule (`mqtt_handler.py`, `*_setup.py`, `repair.py`) entfernt
- Dokumentation und Release-Notizen auf das neue HACS-Repo umgestellt
- Repo- und Anzeigename auf `ha-tsun-inverter` bzw. „TSUN Inverter" umgestellt (vom früheren Arbeitsnamen `ha-tsun-gen3-proxy`)

### Fixed

- MyPy-Fehler durch `ConfigFlowResult` in Home Assistant 2025.1 behoben
- HACS-Validierung durch Repository-Topics (`home-assistant`, `hacs`, `integration`, …) erfüllt
- Geräteidentifikatoren und eindeutige IDs sanitisiert, Config Entry im Koordinator übergeben

## [0.1.0] - 2026-11-21

> Historisch: v0.1.0 war ein Gerüst mit Platzhaltertests und nicht verdrahtetem MQTT-Handler. Die unten aufgeführten Funktionen wurden erst mit 0.2.0 tatsächlich umgesetzt.

### Added

- Initial Home Assistant TSUN-Gen3-Proxy integration
- MQTT connection support for TSUN Gen3/Gen3+ inverters
- 9 sensor entities (rated_power, total_generation_today, total_generation_total, sw_exception, at_command_blocked, mqtt_published, mqtt_received, online, at_rate_limit)
- 1 binary sensor (inverter online/offline status)
- 1 number entity (AT command rate limit)
- 1 select entity (ACL mode: standard/strict/disabled)
- 1 update entity (firmware update support)
- Config flow with user-friendly setup wizard
- Options flow for runtime configuration changes
- MQTT Home Assistant discovery for automatic entity registration
- Diagnostics endpoint
- Repair flow for configuration fixes
- Brand assets for HACS (brand/icon.png)
- Full licensing and attribution documentation (LICENSE, THIRD_PARTY_LICENSES.md, ATTRIBUTION.md)

### Changed

- Repository structure relocated to HACS-compliant `custom_components/tsun/`
- Manifest.json enhanced with all required HACS keys (domain, name, codeowners, config_flow, documentation, integration_type, iot_class, issue_tracker, version, categories)
- License updated from none to Apache-2.0

### Deprecated

- None (initial release)

### Fixed

- None (initial release)

### Security

- None (initial release)
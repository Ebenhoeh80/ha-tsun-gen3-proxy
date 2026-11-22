# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/lang/en/).

## [Unreleased]

## 0.3.0 - 2026-11-22

### Changed

- Options-Default `latest_version` entfernt; die GitHub-Abfrage liefert den aktuellen Release-Stand. Ein Legacy-Wert aus einem alten Config Entry bleibt als Ausweichwert, `DEFAULT_VERSION` ist nur der Startwert bis zur ersten Abfrage.
- Alle Plattformen mit `PARALLEL_UPDATES` versehen und Laufzeitdaten über `entry.runtime_data` statt `hass.data` bereitgestellt.
- Device-Remove-Hook ergänzt, damit entfernte Geräte auch aus der Registrierung verschwinden.
- Numerische Sensoren liefern echte Zahlen statt formatierter Strings; Leistungswerte nutzen die Device-Class `power`, die Update-Entität `firmware`.
- Icons und Entity-Namen kommen aus den Translation-Dateien (`strings.json`, `translations/de.json`, `translations/en.json`).
- Diagnostics enthalten `last_seen` je Knoten und redigieren sensible Werte weiterhin zuverlässig.
- Availability wird pro Knoten berechnet; eine Knoten-Obergrenze und ein Payload-Tiefenlimit begrenzen Speicher und Registry-Wachstum.
- Tests importieren echte Home-Assistant-Klassen mit `pytest-homeassistant`; globale Fake-Module in `sys.modules` wurden entfernt. 61 Tests, Ruff, Ruff-Format, MyPy und Coverage (76 %) lokal grün.
- CI: Root-`pyproject.toml` für Ruff (`line-length = 88`, `select = ["E", "F", "W", "I", "B", "UP"]`), zusätzlicher `ruff format --check`, exakt gepinnte Python-Pakete, gepinnte HACS-/Hassfest-Refs, `permissions: contents: read` und Timeouts für HACS/Hassfest.

### Documentation

- Widersprüchliche Altaussagen (nicht existierende Klasse, nicht verifizierte CI-/Prüfstandsangaben und veraltete Versions-/Fixture-Hinweise) wurden mit Datum und Grund durchgestrichen statt gelöscht.
- Verifikationsstatus: 61 Tests, 76 % Coverage, Ruff-Lint, Ruff-Format und MyPy lokal grün. CI-Lauf `45051181152` für Commit `2e721df` nach dem Push grün (Jobs `test`, `hacs`, `hassfest`); nur nicht-blockierende Hinweise zu Manifest-Kategorien und Node-20-Actions. Die Manifest-Version ist 0.3.0. (bestätigt 22.11.2026)

## [0.2.4] - 2026-11-22

### Added

- Die Update-Entität fragt das neueste GitHub-Release ab (alle 6 Stunden) und zeigt Version, Release-Seite und Beschreibung dynamisch an. Ein manuell gesetzter Wert in `entry.data`/Optionen bleibt als Offline-Fallback maßgeblich.

### Changed

- `at_rate_limit` nutzt jetzt `RestoreNumber`; `acl_mode` kombiniert `SelectEntity` und `RestoreEntity`. Gesetzte Werte überstehen einen HA-Neustart und werden auf gültige Wertebereiche geprüft. ~~Die erste Fassung dieser Notiz nannte `RestoreSelect`.~~ (korrigiert 22.11.2026: `RestoreSelect` existiert in Home Assistant nicht; maßgeblich sind `RestoreNumber` sowie `SelectEntity` + `RestoreEntity`.)
- MQTT-Steuer-Kommandos werden mit `retain=False` veröffentlicht, damit veraltete Befehle nicht nach einem Proxy-Neustart erneut angewendet werden.

### Fixed

- Die Update-Entität zeigt nicht mehr dauerhaft eine statisch konfigurierte Version, sondern den tatsächlich verfügbaren Release-Stand.

## [0.2.3] - 2026-11-22

### Fixed

- Der Einrichtungsdialog nennt jetzt „TSUN Inverter" statt der alten Bezeichnung „TSUN-Gen3-Proxy" (Nutzerfund 22.11.2026); deutsche und englische Fassung sowie `strings.json` sind konsistent. Die Formulierung beschreibt korrekt, dass die Integration Messwerte empfängt.

## [0.2.2] - 2026-11-22

### Changed

- Lizenz der Integration von Apache-2.0 auf MIT umgestellt (Nutzerentscheidung 2026-11-22); die Lizenz des Upstream-TSUN-Gen3-Proxys bleibt unverändert
- Einrichtungsdialog auf eine Bestätigung reduziert: keine Abfrage von MQTT-Host, -Port, Zugangsdaten oder Knoten-ID mehr; die vorhandene HA-MQTT-Integration und die automatische Knotenerkennung werden genutzt
- Number-, Select- und Update-Entitäten werden wie die Sensoren für erkannte Knoten erzeugt; bestehende Einträge mit gespeicherter `node_id` behalten ihr Verhalten
- Upgrade-Hinweis: Wer v0.2.1 mit dem alten Standardknoten `inverter` nutzte, sieht nach dem Update die alte Update-Entität samt zugehörigem Gerät als „nicht verfügbar" in der HA-Entity-Registry. Der Platzhalter wird jetzt ignoriert und die Update-Entität hat eine knotunabhängige Unique-ID. Die verwaisten Einträge können manuell unter „Einstellungen → Geräte & Dienste → Entitäten/Geräte" entfernt werden; neue Erkenntnisse oder automatische Bereinigung sind für diese Version nicht vorgesehen.

### Fixed

- Der Pseudoknoten `proxy` erhält keine Wechselrichter-Summen und keine Steuerungs- oder Update-Entitäten mehr; dort bleiben nur Diagnosesensoren
- Die Update-Entität nutzt eine stabile Unique-ID ohne Knotenbezug, damit nach einem Neustart keine verwaiste zweite Entität entsteht
- Der alte Platzhalter `inverter` wird bei Legacy-Einträgen ignoriert, damit kein Phantom-Gerät entsteht
- Diagnoseausgabe redigiert MQTT-Host, -Benutzer, -Passwort und die Unique-ID auch bei Legacy-Einträgen
- Der Koordinator wartet vor dem MQTT-Abonnement auf den Client (`async_wait_for_mqtt_client`, Vorgabe der Home-Assistant-Dokumentation); ohne Client wird das Setup über `ConfigEntryNotReady` später erneut versucht, statt beim Neustart die ersten Messwerte zu verlieren (Vorbild: HA-Core-Integration `silla_prism`)
- Der Einrichtungsdialog bricht ohne verfügbaren MQTT-Client mit der verständlichen Meldung `mqtt_unavailable` ab, statt einen generischen Setup-Fehler zu erzeugen

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

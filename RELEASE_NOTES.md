# TSUN Inverter 0.2.3 – Release-Hinweise

## Release-Informationen

- **Version:** 0.2.3
- **Datum:** 2026-11-22
- **Repository:** https://github.com/Ebenhoeh80/ha-tsun-inverter
- **Voraussetzung:** Home Assistant 2024.11.0 oder neuer, konfigurierte MQTT-Integration

## Hauptänderungen

Diese Version korrigiert einen Textfehler im Einrichtungsdialog: Dort stand noch die alte Bezeichnung „TSUN-Gen3-Proxy". Jetzt heißt es durchgängig „TSUN Inverter" — in `strings.json`, der deutschen und der englischen Übersetzung. Die Formulierung wurde dabei so angepasst, dass sie korrekt beschreibt, dass die Integration Messwerte **empfängt** (statt sie zu veröffentlichen).

Die Änderungen aus 0.2.2 bleiben unverändert gültig:

Diese Version macht die seit 0.2.1 auf `main` liegenden Änderungen als HACS-Release verfügbar:

- **Einrichtung:** Der Dialog besteht nur noch aus einer Bestätigung. MQTT-Host, -Port, Zugangsdaten und Knoten-ID werden nicht abgefragt; die vorhandene HA-MQTT-Integration wird genutzt und die Knoten kommen aus dem Datenstrom `tsun/#`.
- **Lizenz:** Die Integration steht jetzt unter MIT. Die Lizenz des Upstream-TSUN-Gen3-Proxys bleibt unverändert.
- **Entitäten:** Number, Select und Update werden nur für erkannte Knoten erzeugt. Der Pseudoknoten `proxy` erhält weiterhin nur Diagnosesensoren. Bestehende Einträge mit gespeicherter `node_id` behalten ihr Verhalten; der alte Platzhalter `inverter` wird ignoriert.
- **MQTT-Verfügbarkeit:** Der Koordinator wartet vor dem Abonnieren auf `mqtt.async_wait_for_mqtt_client`; ohne Client wird das Setup über `ConfigEntryNotReady` erneut versucht. Der Einrichtungsdialog bricht ohne MQTT mit der übersetzten Meldung `mqtt_unavailable` ab.
- **Diagnose:** MQTT-Host, -Benutzer, -Passwort und die Unique-ID werden auch bei Legacy-Einträgen redigiert.

## Installation und Upgrade

1. `https://github.com/Ebenhoeh80/ha-tsun-inverter` in HACS unter **Integrationen → Benutzerdefinierte Repositories** hinzufügen (falls noch nicht geschehen).
2. „TSUN Inverter" auf Version 0.2.2 aktualisieren und Home Assistant neu starten.
3. Bei bestehender Installation ist kein erneuter Einrichtungsdialog nötig.

**Upgrade-Hinweis:** Wer 0.2.1 mit dem alten Standardknoten `inverter` nutzte, sieht danach die alte Update-Entität samt zugehörigem Gerät als „nicht verfügbar" in der HA-Entity-Registry. Der Platzhalter wird jetzt ignoriert und die Update-Entität hat eine knotunabhängige Unique-ID. Die verwaisten Einträge können manuell unter **Einstellungen → Geräte & Dienste → Entitäten/Geräte** entfernt werden; eine automatische Bereinigung ist in dieser Version nicht enthalten.

Für eine neue Installation: **Einstellungen → Geräte & Dienste → Integration hinzufügen** → „TSUN Inverter" auswählen und die Einrichtung bestätigen. Host, Port und Zugangsdaten sind nicht nötig.

## Prüfstand

35/35 pytest-Tests, ruff, mypy (19 Dateien) und compileall lokal grün. GitHub-CI `test`, `hacs` und `hassfest` für Commit `59795d9` grün.

## Hinweise

- Das Repository hieß während der Entwicklung `ha-tsun-gen3-proxy` und wurde vor Veröffentlichung in `ha-tsun-inverter` umbenannt; HACS-Einträge mit der alten URL bitte erneuern.
- Veröffentlicht der Proxy selbst MQTT-Discovery, können doppelte Entitäten entstehen. Discovery im Proxy deaktivieren oder die automatisch erzeugten MQTT-Entitäten ignorieren.
- `at_rate_limit` und `acl_mode` senden MQTT-Kommandos, für die der Upstream-Proxy derzeit keine passenden Topics definiert. Die Befehle werden mit `retain=true` veröffentlicht.
- Number und Select sind keine `RestoreEntity`; ihre Werte fallen nach einem Neustart auf den Standardwert zurück.
- Ein HA-Live-Test in einer Installation steht noch aus; die automatisierten Prüfungen sind grün.

## Ältere Versionen

- **0.2.2** (2026-11-22): Lizenz-, UX- und MQTT-Verfügbarkeits-Fixes als HACS-Release verfügbar gemacht.
- **0.2.1** (2026-11-22): Korrektur der PV-Werte aus `tsun/<knoten>/input`, Versionsanzeige und Manifest.
- **0.2.0** (2026-11-22): erste stabile HACS-Version mit echten Entitäten und CI. Prerelease `v0.2.0-rc1` war zwischenzeitlich rot (MyPy `ConfigFlowResult`, fehlende HACS-Topics) und ist ersetzt.
- **0.1.0** (2026-11-21): veröffentlicht im Fork `Ebenhoeh80/tsun-gen3-proxy`, aber funktional nur ein Gerüst mit Platzhaltertests und nicht verdrahtetem MQTT-Handler. Der damalige Release-Text beschrieb Funktionen (aiomqtt, MQTT-Discovery, Repair-Flow), die so nie existierten. Originaltext unverändert erhalten in `raw/projekte/tsun/RELEASE_NOTES.md` und in der Git-Historie des Forks.

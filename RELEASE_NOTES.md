# TSUN Inverter 0.2.4 - Release-Hinweise

## Release-Informationen

- **Version:** 0.2.4
- **Datum:** 2026-11-22
- **Repository:** https://github.com/Ebenhoeh80/ha-tsun-inverter
- **Voraussetzung:** Home Assistant 2024.11.0 oder neuer, konfigurierte MQTT-Integration

## Hauptänderungen

Diese Version verbessert zwei Punkte nach Home-Assistant-Best-Practices:

- **AT-Befehlsrate und Zugriffsmodus:** `at_rate_limit` und `acl_mode` sind jetzt `RestoreNumber` bzw. `RestoreSelect`. Ein gesetzter Wert bleibt nach einem HA-Neustart erhalten; unplausible gespeicherte Werte werden verworfen.
- **Neueste Version:** Die Update-Entität fragt das aktuelle GitHub-Release ab (bei Start und alle 6 Stunden) und zeigt Version, Release-Seite und Beschreibung an. Ein manuell gesetzter Wert in den Optionen bleibt als Offline-Fallback erhalten.
- **Steuer-Kommandos:** MQTT-Befehle werden mit `retain=false` gesendet, damit ein alter Befehl nach einem Proxy-Neustart nicht erneut wirksam wird.

Die Änderungen aus 0.2.2 und 0.2.3 bleiben unverändert gültig.

## Installation und Upgrade

1. `https://github.com/Ebenhoeh80/ha-tsun-inverter` in HACS unter **Integrationen → Benutzerdefinierte Repositories** hinzufügen (falls noch nicht geschehen).
2. "TSUN Inverter" auf Version 0.2.4 aktualisieren und Home Assistant neu starten.
3. Bei bestehender Installation ist kein erneuter Einrichtungsdialog nötig.

**Upgrade-Hinweis:** Wer 0.2.1 mit dem alten Standardknoten `inverter` nutzte, sieht danach die alte Update-Entität samt zugehörigem Gerät als "nicht verfügbar" in der HA-Entity-Registry. Der Platzhalter wird jetzt ignoriert und die Update-Entität hat eine knotunabhängige Unique-ID. Die verwaisten Einträge können manuell unter **Einstellungen → Geräte & Dienste → Entitäten/Geräte** entfernt werden; eine automatische Bereinigung ist in dieser Version nicht enthalten.

Für eine neue Installation: **Einstellungen → Geräte & Dienste → Integration hinzufügen** → "TSUN Inverter" auswählen und die Einrichtung bestätigen. Host, Port und Zugangsdaten sind nicht nötig.

## Prüfstand

43/43 pytest-Tests, ruff, mypy (20 Dateien) und compileall lokal grün. GitHub-CI `test`, `hacs` und `hassfest` für den Release-Commit grün.

## Hinweise

- Das Repository hieß während der Entwicklung `ha-tsun-gen3-proxy` und wurde vor Veröffentlichung in `ha-tsun-inverter` umbenannt; HACS-Einträge mit der alten URL bitte erneuern.
- Veröffentlicht der Proxy selbst MQTT-Discovery, können doppelte Entitäten entstehen. Discovery im Proxy deaktivieren oder die automatisch erzeugten MQTT-Entitäten ignorieren.
- `at_rate_limit` und `acl_mode` senden MQTT-Kommandos, für die der Upstream-Proxy derzeit keine passenden Topics definiert. Die Befehle sind daher wirkungslos, werden aber nicht mehr retainiert.
- Beim HA-Live-Check 22.11.2026 war die Integration geladen, es kamen jedoch keine `tsun/#`-Daten an. Ohne Datenstrom entstehen keine Sensoren oder Geräte – das ist erwartungskonform. Die Update-Entität in der Installation stammt von HACS (Marketplace-Plattform), nicht von dieser Integration.

## Ältere Versionen

- **0.2.3** (2026-11-22): Bezeichnung im Einrichtungsdialog auf "TSUN Inverter" korrigiert.
- **0.2.2** (2026-11-22): Lizenz-, UX- und MQTT-Verfägbarkeits-Fixes als HACS-Release verfügbar gemacht.
- **0.2.1** (2026-11-22): Korrektur der PV-Werte aus `tsun/<knoten>/input`, Versionsanzeige und Manifest.
- **0.2.0** (2026-11-22): erste stabile HACS-Version mit echten Entitäten und CI. Prerelease `v0.2.0-rc1` war zwischenzeitlich rot (MyPy `ConfigFlowResult`, fehlende HACS-Topics) und ist ersetzt.
- **0.1.0** (2026-11-21): veröffentlicht im Fork `Ebenhoeh80/tsun-gen3-proxy`, aber funktional nur ein Gerüst mit Platzhaltertests und nicht verdrahtetem MQTT-Handler. Der damalige Release-Text beschrieb Funktionen (aiomqtt, MQTT-Discovery, Repair-Flow), die so nie existierten. Originaltext unverändert erhalten in `raw/projekte/tsun/RELEASE_NOTES.md` und in der Git-Historie des Forks.

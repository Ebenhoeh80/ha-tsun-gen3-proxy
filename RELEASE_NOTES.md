# TSUN Inverter – Release-Hinweise

## 0.3.0 - 2026-11-22

- **Version:** 0.3.0
- **Datum:** 2026-11-22
- **Repository:** https://github.com/Ebenhoeh80/ha-tsun-inverter
- **Manifest-Version:** 0.3.0

### Hauptänderungen

- Options-Default `latest_version` entfernt; die Update-Abfrage funktioniert jetzt ohne statischen Fallback-Wert und liefert den aktuellen Release-Stand.
- Koordinator mit `PARALLEL_UPDATES` und Laufzeitdaten über `entry.runtime_data` statt `hass.data`.
- Device-Remove-Hook ergänzt, damit entfernte Geräte auch aus der Registrierung verschwinden.
- Numerische Sensoren liefern echte Zahlen statt formatierter Strings; Leistungswerte nutzen die Device-Class `power`, die Update-Entität `firmware`.
- Icons und Entity-Namen kommen aus den Translation-Dateien.
- Diagnostics enthalten `last_seen` je Knoten und redigieren sensible Werte weiterhin zuverlässig.
- Availability wird pro Knoten berechnet; Knoten-Obergrenze und Payload-Tiefenlimit begrenzen Registry- und Speicherwachstum.
- Tests importieren echte Home-Assistant-Klassen mit `pytest-homeassistant`; globale Fake-Module in `sys.modules` wurden entfernt.
- CI: Root-`pyproject.toml` für Ruff, zusätzlicher `ruff format --check`, exakt gepinnte Python-Pakete, gepinnte HACS-/Hassfest-Refs, `permissions: contents: read` und Timeouts.
- Dokumentationskorrektur: widersprüchliche Altaussagen aus 0.2.x wurden mit Datum und Grund durchgestrichen, nicht gelöscht.

### Prüfstand / Verifikation

Lokal grün: 61 Tests, Ruff-Lint, Ruff-Format, MyPy und Coverage (76 % der Integrationsdateien). Dieselben Prüfungen sind als CI-Gates hinterlegt. Ein bestätigter grüner CI-Lauf für den Release-Commit lag zum Zeitpunkt des Tags noch nicht vor; diese Hinweise behaupten daher keinen grünen CI-Status.

### Installation und Upgrade

1. `https://github.com/Ebenhoeh80/ha-tsun-inverter` in HACS unter **Integrationen → Benutzerdefinierte Repositories** hinzufügen (falls noch nicht geschehen).
2. „TSUN Inverter" auf Version 0.3.0 aktualisieren und Home Assistant neu starten.
3. Bei bestehender Installation ist kein erneuter Einrichtungsdialog nötig.

## 0.2.4 - 2026-11-22

### Release-Informationen

- **Version:** 0.2.4
- **Datum:** 2026-11-22
- **Repository:** https://github.com/Ebenhoeh80/ha-tsun-inverter
- **Voraussetzung:** Home Assistant 2024.11.0 oder neuer, konfigurierte MQTT-Integration

### Hauptänderungen

Diese Version verbessert ~~zwei Punkte~~ (korrigiert 22.11.2026: es sind drei Punkte) nach Home-Assistant-Best-Practices:

- **AT-Befehlsrate und Zugriffsmodus:** `at_rate_limit` nutzt jetzt `RestoreNumber`, `acl_mode` kombiniert `SelectEntity` und `RestoreEntity`. Ein gesetzter Wert bleibt nach einem HA-Neustart erhalten; unplausible gespeicherte Werte werden verworfen. ~~Die erste Fassung dieser Hinweise nannte `RestoreSelect`.~~ (korrigiert 22.11.2026: `RestoreSelect` existiert in Home Assistant nicht; maßgeblich sind `RestoreNumber` sowie `SelectEntity` + `RestoreEntity`.)
- **Neueste Version:** Die Update-Entität fragt das aktuelle GitHub-Release ab (bei Start und alle 6 Stunden) und zeigt Version, Release-Seite und Beschreibung an. Ein manuell gesetzter Wert in den Optionen bleibt als Offline-Fallback erhalten.
- **Steuer-Kommandos:** MQTT-Befehle werden mit `retain=false` gesendet, damit ein alter Befehl nach einem Proxy-Neustart nicht erneut wirksam wird.

Die Änderungen aus 0.2.2 und 0.2.3 bleiben unverändert gültig.

### Installation und Upgrade

1. `https://github.com/Ebenhoeh80/ha-tsun-inverter` in HACS unter **Integrationen → Benutzerdefinierte Repositories** hinzufügen (falls noch nicht geschehen).
2. "TSUN Inverter" auf Version 0.2.4 aktualisieren und Home Assistant neu starten.
3. Bei bestehender Installation ist kein erneuter Einrichtungsdialog nötig.

**Upgrade-Hinweis:** Wer 0.2.1 mit dem alten Standardknoten `inverter` nutzte, sieht danach die alte Update-Entität samt zugehörigem Gerät als "nicht verfügbar" in der HA-Entity-Registry. Der Platzhalter wird jetzt ignoriert und die Update-Entität hat eine knotunabhängige Unique-ID. Die verwaisten Einträge können manuell unter **Einstellungen → Geräte & Dienste → Entitäten/Geräte** entfernt werden; eine automatische Bereinigung ist in dieser Version nicht enthalten.

Für eine neue Installation: **Einstellungen → Geräte & Dienste → Integration hinzufügen** → "TSUN Inverter" auswählen und die Einrichtung bestätigen. Host, Port und Zugangsdaten sind nicht nötig.

### Prüfstand

~~43/43 pytest-Tests, ruff, mypy (20 Dateien) und compileall lokal grün. GitHub-CI `test`, `hacs` und `hassfest` für den Release-Commit grün.~~ (korrigiert 22.11.2026: die Zahlen und der grüne CI-Status konnten für 0.2.4 nicht verifiziert werden; für diesen Stand liegt kein bestätigter CI-Lauf vor.)

### Hinweise

- Das Repository hieß während der Entwicklung `ha-tsun-gen3-proxy` und wurde vor Veröffentlichung in `ha-tsun-inverter` umbenannt; HACS-Einträge mit der alten URL bitte erneuern.
- Veröffentlicht der Proxy selbst MQTT-Discovery, können doppelte Entitäten entstehen. Discovery im Proxy deaktivieren oder die automatisch erzeugten MQTT-Entitäten ignorieren.
- `at_rate_limit` und `acl_mode` senden MQTT-Kommandos, für die der Upstream-Proxy derzeit keine passenden Topics definiert. Die Befehle sind daher wirkungslos, werden aber nicht mehr retainiert.
- Beim HA-Live-Check 22.11.2026 war die Integration geladen, es kamen jedoch keine `tsun/#`-Daten an. Ohne Datenstrom entstehen keine Sensoren oder Geräte – das ist erwartungskonform. Die Update-Entität in der Installation stammt von HACS (Marketplace-Plattform), nicht von dieser Integration.

### Ältere Versionen

- **0.2.3** (2026-11-22): Bezeichnung im Einrichtungsdialog auf "TSUN Inverter" korrigiert.
- **0.2.2** (2026-11-22): Lizenz-, UX- und MQTT-Verfägbarkeits-Fixes als HACS-Release verfügbar gemacht.
- **0.2.1** (2026-11-22): Korrektur der PV-Werte aus `tsun/<knoten>/input`, Versionsanzeige und Manifest.
- **0.2.0** (2026-11-22): erste stabile HACS-Version mit echten Entitäten und CI. Prerelease `v0.2.0-rc1` war zwischenzeitlich rot (MyPy `ConfigFlowResult`, fehlende HACS-Topics) und ist ersetzt.
- **0.1.0** (2026-11-21): veröffentlicht im Fork `Ebenhoeh80/tsun-gen3-proxy`, aber funktional nur ein Gerüst mit Platzhaltertests und nicht verdrahtetem MQTT-Handler. Der damalige Release-Text beschrieb Funktionen (aiomqtt, MQTT-Discovery, Repair-Flow), die so nie existierten. Originaltext unverändert erhalten in `raw/projekte/tsun/RELEASE_NOTES.md` und in der Git-Historie des Forks.

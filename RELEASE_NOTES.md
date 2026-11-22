# TSUN Inverter 0.2.1 – Release-Hinweise

## Release-Informationen

- **Version:** 0.2.1
- **Datum:** 2026-11-22
- **Repository:** https://github.com/Ebenhoeh80/ha-tsun-inverter
- **Voraussetzung:** Home Assistant 2024.11.0 oder neuer, konfigurierte MQTT-Integration

## Hauptänderungen

Diese Version korrigiert drei inhaltliche Fehler der stabilen Erstversion 0.2.0:

- **Erzeugungswerte:** Die verschachtelten PV-Werte auf `tsun/<knoten>/input` (`pv1` … `pv6`) konnten die Wechselrichter-Summen aus `tsun/<knoten>/total` überschreiben. Messwerte werden jetzt anhand der Topic-Gruppe zugeordnet: `Rated_Power` aus `inverter`, `Daily_Generation`/`Total_Generation` aus `total`, Proxy-Zähler aus `proxy`.
- **Versionsanzeige:** `const.VERSION` und das Manifest standen auf 0.1.0 bzw. 0.2.0; die Update-Entität meldet jetzt konsistent 0.2.1 und berücksichtigt auch den Wert aus `entry.data`.
- **Manifest:** Der nicht zulässige Schlüssel `keywords` wurde entfernt. `hassfest` läuft jetzt als zusätzlicher CI-Job neben ruff, mypy, pytest und `hacs/action`.

Die Grundfunktionen bleiben unverändert: MQTT-Anbindung über die Home-Assistant-Integration, `DataUpdateCoordinator` mit Push-Updates, echte Entitäten (Sensor, Binärsensor, Number, Select, Update), Konfigurationsdialog mit Unique-ID, Options-Flow und Passwort-Redaktion in der Diagnose, Deutsch und Englisch.

## Installation

1. `https://github.com/Ebenhoeh80/ha-tsun-inverter` in HACS unter **Integrationen → Benutzerdefinierte Repositories** hinzufügen.
2. „TSUN Inverter" installieren und Home Assistant neu starten.
3. **Einstellungen → Geräte & Dienste → Integration hinzufügen** aufrufen und die Knoten-ID angeben.

Hinweis: Host, Port und Zugangsdaten im Konfigurationsdialog werden nicht für die MQTT-Verbindung verwendet – diese läuft ausschließlich über die konfigurierte Home-Assistant-MQTT-Integration. Es genügt die Knoten-ID; die übrigen Felder sind für die eindeutige ID und spätere Optionen reserviert.

## Hinweise

- Das Repository hieß während der Entwicklung `ha-tsun-gen3-proxy` und wurde vor Veröffentlichung in `ha-tsun-inverter` umbenannt; HACS-Einträge mit der alten URL bitte erneuern.
- Veröffentlicht der Proxy selbst MQTT-Discovery, können doppelte Entitäten entstehen. Discovery im Proxy deaktivieren oder die automatisch erzeugten MQTT-Entitäten ignorieren.
- `at_rate_limit` und `acl_mode` senden MQTT-Kommandos, für die der Upstream-Proxy derzeit keine passenden Topics definiert. Die Befehle werden mit `retain=true` veröffentlicht.
- Number und Select sind keine `RestoreEntity`; ihre Werte fallen nach einem Neustart auf den Standardwert zurück.
- Ein HA-Live-Test in einer Installation steht noch aus; die automatisierten Prüfungen (ruff, mypy, pytest, HACS, hassfest) sind grün.

## Ältere Versionen

- **0.2.0** (2026-11-22): erste stabile HACS-Version mit echten Entitäten und CI. Prerelease `v0.2.0-rc1` war zwischenzeitlich rot (MyPy `ConfigFlowResult`, fehlende HACS-Topics) und ist ersetzt.
- **0.1.0** (2026-11-21): veröffentlicht im Fork `Ebenhoeh80/tsun-gen3-proxy`, aber funktional nur ein Gerüst mit Platzhaltertests und nicht verdrahtetem MQTT-Handler. Der damalige Release-Text beschrieb Funktionen (aiomqtt, MQTT-Discovery, Repair-Flow), die so nie existierten. Originaltext unverändert erhalten in `raw/projekte/tsun/RELEASE_NOTES.md` und in der Git-Historie des Forks.

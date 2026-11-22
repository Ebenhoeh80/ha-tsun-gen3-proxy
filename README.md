# TSUN-Gen3-Proxy – Home-Assistant-Integration

[![HACS Custom Repository](https://img.shields.io/badge/HACS-custom-orange.svg)](https://hacs.xyz/docs/repositories)

Home-Assistant-Integration für TSUN-Gen3/Gen3+-Wechselrichter und Batterien. Sie liest die Messwerte des [TSUN-Gen3-Proxys](https://github.com/s-allius/tsun-gen3-proxy) über MQTT aus und stellt sie als native Home-Assistant-Entitäten bereit.

## Voraussetzungen

- Home Assistant 2024.1.0 oder neuer
- Die MQTT-Integration von Home Assistant muss konfiguriert sein
- Ein laufender TSUN-Gen3-Proxy, der seine Daten an denselben Broker veröffentlicht (Standard-Topic `tsun/<knoten_id>/<gruppe>`)

## Installation über HACS

1. HACS → **Integrationen** → Menü (⋮) → **Benutzerdefinierte Repositories**.
2. `https://github.com/Ebenhoeh80/ha-tsun-gen3-proxy` als Typ **Integration** hinzufügen.
3. „TSUN-Gen3-Proxy" suchen, installieren und Home Assistant neu starten.
4. **Einstellungen → Geräte & Dienste → Integration hinzufügen** → „TSUN-Gen3-Proxy" auswählen.
5. MQTT-Host, -Port und optional Benutzer/Passwort sowie die Knoten-ID eingeben.

## Manuelle Installation

`custom_components/tsun/` in das Verzeichnis `config/custom_components/` der Home-Assistant-Installation kopieren und HA neu starten.

## Bereitgestellte Entitäten

| Plattform | Entität |
|---|---|
| Sensor | Nennleistung, Tageserzeugung, Gesamterzeugung |
| Sensor (Diagnose) | Softwarefehler, blockierte AT-Befehle, MQTT-Zähler |
| Binärsensor | Online-Status |
| Number | AT-Befehlsrate |
| Select | AT-Zugriffsmodus |
| Update | Bekannte Version |

Neue Knoten werden automatisch erkannt, sobald der Proxy Daten veröffentlicht.

## Hinweis zu doppelten Entitäten

Der Proxy kann selbst MQTT-Discovery-Nachrichten veröffentlichen. Wenn beide Mechanismen aktiv sind, entstehen doppelte Entitäten. Entweder die Discovery im Proxy deaktivieren (`ha.discovery_prefix` auf einen unbenutzten Wert setzen) oder die automatisch erzeugten MQTT-Entitäten in Home Assistant ignorieren.

## Entwicklung

```bash
python -m ruff check custom_components/tsun
python -m mypy custom_components/tsun --ignore-missing-imports --explicit-package-bases
python -m pytest custom_components/tsun/tests -q
```

Die Unit-Tests prüfen die reine Logik mit Stubs. Für einen vollständigen HA-Testlauf wird `pytest-homeassistant-custom-component` benötigt.

## Lizenz

Apache-2.0. Der TSUN-Gen3-Proxy selbst bleibt unter seiner ursprünglichen Lizenz.

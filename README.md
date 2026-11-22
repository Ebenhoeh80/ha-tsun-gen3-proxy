# TSUN Inverter – Home-Assistant-Integration

[![HACS Custom Repository](https://img.shields.io/badge/HACS-custom-orange.svg)](https://hacs.xyz/docs/repositories)

Home-Assistant-Integration für TSUN-Gen3/Gen3+-Wechselrichter und Batterien. Sie liest die Messwerte des [TSUN-Gen3-Proxys](https://github.com/s-allius/tsun-gen3-proxy) über MQTT aus und stellt sie als native Home-Assistant-Entitäten bereit.

## Voraussetzungen

- Home Assistant 2024.11.0 oder neuer (wegen `ConfigFlowResult` und Koordinator-Config-Entry)
- Die MQTT-Integration von Home Assistant muss konfiguriert sein
- Ein laufender TSUN-Gen3-Proxy, der seine Daten an denselben Broker veröffentlicht (Standard-Topic `tsun/<knoten_id>/<gruppe>`)

## Installation über HACS

1. HACS → **Integrationen** → Menü (⋮) → **Benutzerdefinierte Repositories**.
2. `https://github.com/Ebenhoeh80/ha-tsun-inverter` als Typ **Integration** hinzufügen.
3. „TSUN Inverter" suchen, installieren und Home Assistant neu starten.
4. **Einstellungen → Geräte & Dienste → Integration hinzufügen** → „TSUN Inverter" auswählen.
5. Die Einrichtung bestätigen. Host, Port, Zugangsdaten und Knoten-ID sind nicht nötig: Die Verbindung läuft über die bereits konfigurierte Home-Assistant-MQTT-Integration, die Wechselrichter werden automatisch erkannt.

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
| Update | Bekannte Version der Integration |

Neue Knoten werden automatisch erkannt, sobald der Proxy Daten veröffentlicht. Es werden höchstens 16 Knoten übernommen; der konfigurierte Knoten hat Vorrang.

> **Hinweis zu Number/Select:** Die beiden Steuerelemente senden die Topics `set_at_rate_limit` und `set_acl_mode` an den Proxy. Für die derzeit eingesetzte Upstream-Version ist keine verlässliche Wirkung dieser Befehle dokumentiert. Solange der Proxy keine Bestätigung zurückmeldet, dienen die Entitäten nur als lokale Merkwerte und können die tatsächliche Konfiguration des Wechselrichters nicht ändern. Ein Publish-Fehler wird geloggt und der Wert nicht optimistisch übernommen.

## Hinweis zu doppelten Entitäten

Der Proxy kann selbst MQTT-Discovery-Nachrichten veröffentlichen. Wenn beide Mechanismen aktiv sind, entstehen doppelte Entitäten. Entweder die Discovery im Proxy deaktivieren (`ha.discovery_prefix` auf einen unbenutzten Wert setzen) oder die automatisch erzeugten MQTT-Entitäten in Home Assistant ignorieren.

## Entwicklung

Lokale Prüfung und GitHub-CI verwenden dieselben gepinnten Werkzeuge (Ruff 0.17.6, MyPy 2.4.1, pytest 9.0.3, Home Assistant 2026.11.2). Home Assistant 2026.11 verlangt Python ≥ 3.14.2. Die Root-`pyproject.toml` enthält die Ruff-Regeln, Formatierungsoptionen und `asyncio_mode = "auto"` für `pytest-homeassistant`.

```bash
python -m pip install \
  coverage==7.17.4 \
  pytest==9.0.3 \
  pytest-asyncio==1.4.0 \
  ruff==0.17.6 \
  mypy==2.4.1 \
  homeassistant==2026.11.2 \
  pytest-homeassistant==2026.11.2 \
  probatio==0.13.0 \
  voluptuous==0.16.0
```

```bash
ruff check custom_components/tsun
ruff format --check custom_components/tsun
mypy custom_components/tsun --ignore-missing-imports --explicit-package-bases
coverage run --source=custom_components/tsun --omit=*/tests/* \
  -m pytest custom_components/tsun/tests -q --tb=short
coverage report -m
```

Die Tests importieren echte Home-Assistant-Klassen und laufen mit `pytest-homeassistant` (2026.11.2). Globale Fake-Module in `sys.modules` gibt es bewusst nicht; HA-Objekte werden dort, wo nötig, gezielt mit `unittest.mock` ersetzt. `--source` wird als Dateipfad angegeben: als Paketname würde Coverage `custom_components.tsun` vor Messbeginn importieren und fälschlich 0 % melden.

## Lizenz

MIT. Der TSUN-Gen3-Proxy selbst bleibt unter seiner ursprünglichen Lizenz.

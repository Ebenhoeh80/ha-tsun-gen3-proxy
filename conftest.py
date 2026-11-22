"""Gemeinsame pytest-Konfiguration für die TSUN-Integration.

Bewusst werden hier KEINE Fake-Module in ``sys.modules`` installiert. Die
Tests laufen gegen die echte Home-Assistant-Installation aus der CI, damit
Schema-, Typ- und Entity-Verträge tatsächlich geprüft werden. Reine
Logiktests dürfen HA-Objekte gezielt mit ``unittest.mock`` ersetzen – aber
nie durch globale Stubs, die Importfehler verdecken.
"""

import json
from dataclasses import dataclass
from datetime import date

from src.core.audit import serialiser_etat


def test_serialiser_etat_none():
    assert serialiser_etat(None) is None


def test_serialiser_etat_dataclass_simple():
    @dataclass
    class Exemple:
        id: int
        nom: str

    resultat = serialiser_etat(Exemple(id=1, nom="Test"))
    assert json.loads(resultat) == {"id": 1, "nom": "Test"}


def test_serialiser_etat_dataclass_avec_date():
    @dataclass
    class ExempleDate:
        id: int
        jour: date

    resultat = serialiser_etat(ExempleDate(id=1, jour=date(2026, 7, 8)))
    assert json.loads(resultat) == {"id": 1, "jour": "2026-07-08"}

"""Tests d'intégration des endpoints /hippodromes et /disciplines — cf. L007 §4.1."""

from src.models.referentiels import Discipline


def test_list_hippodromes(client):
    reponse = client.get("/api/v1/hippodromes")
    assert reponse.status_code == 200
    noms = [h["nom"] for h in reponse.json()["data"]]
    assert "ParisLongchamp" in noms


def test_list_disciplines(client, repos):
    repos["referentiel"].seed_discipline(Discipline(libelle="Plat"))
    repos["referentiel"].seed_discipline(Discipline(libelle="Trot Attelé"))

    reponse = client.get("/api/v1/disciplines")

    assert reponse.status_code == 200
    libelles = [d["libelle"] for d in reponse.json()["data"]]
    assert "Plat" in libelles
    assert "Trot Attelé" in libelles

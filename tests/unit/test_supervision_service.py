import dataclasses
from datetime import datetime, timedelta, timezone

from src.services.supervision_service import SupervisionService
from tests.integration.fakes import FakeTacheRepository


def test_etat_base_de_donnees_ko_sans_lever():
    """Une base indisponible ne doit jamais faire planter la supervision — cf.
    `_ping_db`, seul `psycopg.Error` est attrapé."""
    demarrage = datetime.now(timezone.utc) - timedelta(hours=2)
    service = SupervisionService("postgresql://invalide@localhost:1/inexistant", "data/sauvegardes", FakeTacheRepository(), demarrage)

    etat = service.etat()

    assert etat.base_de_donnees_ok is False
    assert etat.latence_db_ms is None


def test_etat_compte_les_echecs_recents_uniquement():
    tache_repo = FakeTacheRepository()
    tache_recente = tache_repo.demarrer("sauvegarde_base", categorie="sauvegarde")
    tache_repo.terminer(tache_recente.id, "echec")
    tache_ancienne = tache_repo.demarrer("sauvegarde_base", categorie="sauvegarde")
    tache_repo.taches[tache_ancienne.id] = dataclasses.replace(
        tache_repo.taches[tache_ancienne.id], debut=datetime.now(timezone.utc) - timedelta(hours=48), statut="echec"
    )

    demarrage = datetime.now(timezone.utc)
    service = SupervisionService("postgresql://invalide@localhost:1/inexistant", "data/sauvegardes", tache_repo, demarrage)

    etat = service.etat()

    assert etat.taches_en_echec_24h == 1


def test_uptime_secondes_coherent_avec_demarrage():
    demarrage = datetime.now(timezone.utc) - timedelta(hours=1)
    service = SupervisionService("postgresql://invalide@localhost:1/inexistant", "data/sauvegardes", FakeTacheRepository(), demarrage)

    etat = service.etat()

    assert 3599 <= etat.uptime_secondes <= 3610

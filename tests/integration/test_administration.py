"""Tests d'intégration du module Administration (L018 §10) — journaux,
automatisations, sauvegardes, versions, paramètres, supervision. Utilise le
client par défaut (utilisateur Administrateur fictif, cf. conftest.py) sauf
pour le test RBAC dédié."""

from datetime import date
from pathlib import Path

from api.dependencies.auth import get_utilisateur_courant
from api.main import app
from src.models.course import Cheval, Cote, Course, Partant, Reunion
from src.models.statistique import StatistiqueGlobale
from src.models.technique import Parametre, Version
from src.models.utilisateur import Role, Utilisateur
from src.services.collecte_service import RapportCollecte


def test_toutes_les_routes_administration_refusent_role_non_administrateur(client):
    role_analyste = Role(id=2, nom="Analyste")
    utilisateur_analyste = Utilisateur(id=2, login="analyste", mot_de_passe="", role_id=2)
    app.dependency_overrides[get_utilisateur_courant] = lambda: (utilisateur_analyste, role_analyste)

    assert client.get("/api/v1/administration/journaux").status_code == 403
    assert client.get("/api/v1/administration/parametres").status_code == 403
    assert client.get("/api/v1/administration/supervision").status_code == 403
    assert client.post("/api/v1/administration/automatisations/collecte").status_code == 403


# -- Journaux -------------------------------------------------------------------


def test_list_journaux_filtre_par_niveau(client, repos):
    repos["journal"].enregistrer("WARNING", "Un avertissement", composant="api.errors")
    repos["journal"].enregistrer("ERROR", "Une erreur", composant="api.errors")

    reponse = client.get("/api/v1/administration/journaux", params={"niveau": "ERROR"})

    assert reponse.status_code == 200
    lignes = reponse.json()["data"]
    assert len(lignes) == 1
    assert lignes[0]["niveau"] == "ERROR"


# -- Automatisations --------------------------------------------------------------


def test_declencher_collecte_journalise_une_tache_et_un_audit(client, repos):
    repos["collecte"].rapport = RapportCollecte(nb_reunions=1, nb_courses=3, nb_partants=20)

    reponse = client.post("/api/v1/administration/automatisations/collecte")

    assert reponse.status_code == 200
    corps = reponse.json()["data"]
    assert corps["nb_courses"] == 3
    taches = repos["tache"].lister(categorie="automatisation")
    assert len(taches) == 1
    assert taches[0].statut == "succes"
    assert repos["audit"].entrees[-1].action == "automatisation_collecte"


def test_declencher_analyse_jour_relance_les_courses_du_jour(client, repos):
    reunion = repos["course"].create_reunion(Reunion(date=date.today(), hippodrome_id=1, numero=1))
    course = repos["course"].create_course(Course(reunion_id=reunion.id, numero=1, nom="Prix Test"))
    cheval = repos["course"].create_cheval(Cheval(nom="Cheval Test"))
    partant = repos["course"].create_partant(Partant(course_id=course.id, cheval_id=cheval.id, numero=1))
    repos["course"].create_cote(Cote(partant_id=partant.id, operateur="PMU", cote=3.0))

    reponse = client.post("/api/v1/administration/automatisations/analyse-jour")

    assert reponse.status_code == 200
    corps = reponse.json()["data"]
    assert corps["nb_courses"] == 1
    assert corps["nb_erreurs"] == 0


def test_declencher_statistiques_recalcule_et_journalise(client, repos):
    repos["statistiques"].a_calculer_globale = StatistiqueGlobale(nb_courses=0, nb_jouees=0)

    reponse = client.post("/api/v1/administration/automatisations/statistiques")

    assert reponse.status_code == 200
    taches = repos["tache"].lister(categorie="automatisation")
    assert any(t.nom == "calcul_statistiques" and t.statut == "succes" for t in taches)


# -- Sauvegardes ------------------------------------------------------------------


def test_declencher_sauvegarde_reussie(client, repos, monkeypatch):
    def _fausse_sauvegarde(database_url, repertoire):
        return Path("/tmp/turfia_test.dump"), 1234

    monkeypatch.setattr("scripts.sauvegarder_base.executer_sauvegarde", _fausse_sauvegarde)

    reponse = client.post("/api/v1/administration/sauvegardes")

    assert reponse.status_code == 200
    corps = reponse.json()["data"]
    assert corps["statut"] == "succes"
    assert "1234" in corps["commentaire"]
    assert repos["audit"].entrees[-1].action == "sauvegarde_manuelle"


def test_declencher_sauvegarde_echouee_retourne_500_et_journalise_echec(client, repos, monkeypatch):
    import subprocess

    def _sauvegarde_en_echec(database_url, repertoire):
        raise subprocess.CalledProcessError(1, ["pg_dump"], stderr=b"erreur simulee")

    monkeypatch.setattr("scripts.sauvegarder_base.executer_sauvegarde", _sauvegarde_en_echec)

    reponse = client.post("/api/v1/administration/sauvegardes")

    assert reponse.status_code == 500
    taches = repos["tache"].lister(categorie="sauvegarde")
    assert taches[0].statut == "echec"


def test_list_sauvegardes_vide_par_defaut(client):
    reponse = client.get("/api/v1/administration/sauvegardes")
    assert reponse.status_code == 200
    assert reponse.json()["data"] == []


# -- Versions -----------------------------------------------------------------------


def test_list_versions(client, repos):
    repos["version"].creer(Version(version="0.2.0", commit_git="abc123", branche="develop"))

    reponse = client.get("/api/v1/administration/versions")

    assert reponse.status_code == 200
    lignes = reponse.json()["data"]
    assert len(lignes) == 1
    assert lignes[0]["version"] == "0.2.0"


# -- Paramètres -----------------------------------------------------------------------


def test_list_et_patch_parametre(client, repos):
    repos["parametre"].seed(Parametre(cle="poids_score.marche", valeur="1.0", type="Decimal"))

    reponse = client.get("/api/v1/administration/parametres")
    assert reponse.status_code == 200
    assert len(reponse.json()["data"]) == 1

    reponse = client.patch("/api/v1/administration/parametres/poids_score.marche", json={"valeur": "2.5"})
    assert reponse.status_code == 200
    assert reponse.json()["data"]["valeur"] == "2.5"
    assert repos["audit"].entrees[-1].action == "modification_parametre"


def test_patch_parametre_inconnu_retourne_404(client):
    reponse = client.patch("/api/v1/administration/parametres/inconnu.cle", json={"valeur": "1"})
    assert reponse.status_code == 404


# -- Supervision --------------------------------------------------------------------


def test_get_supervision(client):
    reponse = client.get("/api/v1/administration/supervision")

    assert reponse.status_code == 200
    corps = reponse.json()["data"]
    assert corps["base_de_donnees_ok"] is True
    assert corps["taches_en_echec_24h"] == 0

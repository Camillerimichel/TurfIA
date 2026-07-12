"""Tests d'intégration du module Administration (L018 §10) — journaux,
automatisations, sauvegardes, versions, paramètres, supervision. Utilise le
client par défaut (utilisateur Administrateur fictif, cf. conftest.py) sauf
pour le test RBAC dédié."""

from datetime import date, datetime, timedelta
from pathlib import Path

from api.dependencies.auth import get_utilisateur_courant
from api.main import app
from src.models.analyse import ControleRoi
from src.models.course import Cheval, Cote, Course, Partant, Resultat, Reunion
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
    assert client.post("/api/v1/administration/automatisations/gains").status_code == 403
    assert client.get("/api/v1/administration/cron").status_code == 403
    assert client.get("/api/v1/administration/cron/journal").status_code == 403
    assert (
        client.post(
            "/api/v1/administration/rejeu",
            json={"version_modele": "x", "date_debut": "2026-01-01", "date_fin": "2026-01-01"},
        ).status_code
        == 403
    )


# -- Tableau de bord Cron ---------------------------------------------------------


def test_list_cron_sans_execution_retourne_derniere_tache_null(client):
    reponse = client.get("/api/v1/administration/cron")

    assert reponse.status_code == 200
    lignes = reponse.json()["data"]
    assert [ligne["nom"] for ligne in lignes] == [
        "collecte_programme_jour", "analyse_courses_jour", "calcul_statistiques",
    ]
    assert all(ligne["derniere_tache"] is None for ligne in lignes)


def test_list_cron_reflete_la_derniere_execution_par_nom(client, repos):
    repos["tache"].demarrer("collecte_programme_jour", categorie="automatisation")
    tache = repos["tache"].demarrer("collecte_programme_jour", categorie="automatisation")
    repos["tache"].terminer(tache.id, "succes", commentaire="ok")

    reponse = client.get("/api/v1/administration/cron")

    assert reponse.status_code == 200
    ligne = next(l for l in reponse.json()["data"] if l["nom"] == "collecte_programme_jour")
    assert ligne["derniere_tache"]["id"] == tache.id
    assert ligne["derniere_tache"]["statut"] == "succes"


def test_get_journal_cron_lit_les_fichiers_de_log(client, tmp_path, monkeypatch):
    fichier_sortie = tmp_path / "rafraichir_et_analyser.log"
    fichier_erreurs = tmp_path / "rafraichir_et_analyser.err.log"
    fichier_sortie.write_text("ligne de sortie\n", encoding="utf-8")
    fichier_erreurs.write_text("ligne d'erreur\n", encoding="utf-8")

    import api.routes.administration as administration_routes

    monkeypatch.setattr(administration_routes, "CHEMIN_JOURNAL_CRON", fichier_sortie)
    monkeypatch.setattr(administration_routes, "CHEMIN_JOURNAL_CRON_ERREURS", fichier_erreurs)

    reponse = client.get("/api/v1/administration/cron/journal")

    assert reponse.status_code == 200
    corps = reponse.json()["data"]
    assert corps["sortie"] == "ligne de sortie\n"
    assert corps["erreurs"] == "ligne d'erreur\n"


def test_get_journal_cron_fichiers_absents_retourne_chaines_vides(client, tmp_path, monkeypatch):
    import api.routes.administration as administration_routes

    monkeypatch.setattr(administration_routes, "CHEMIN_JOURNAL_CRON", tmp_path / "absent.log")
    monkeypatch.setattr(administration_routes, "CHEMIN_JOURNAL_CRON_ERREURS", tmp_path / "absent.err.log")

    reponse = client.get("/api/v1/administration/cron/journal")

    assert reponse.status_code == 200
    corps = reponse.json()["data"]
    assert corps == {"sortie": "", "erreurs": ""}


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


def test_declencher_analyse_jour_relance_une_deuxieme_fois_cree_une_nouvelle_version(client, repos):
    """Non-régression : chaque déclenchement (manuel ou automatisation
    horaire, cf. L033) doit viser une nouvelle version plutôt que de rejouer
    la même — jamais de conflit, la décision peut changer d'une heure à
    l'autre dans les deux sens."""
    reunion = repos["course"].create_reunion(Reunion(date=date.today(), hippodrome_id=1, numero=1))
    course = repos["course"].create_course(Course(reunion_id=reunion.id, numero=1, nom="Prix Test"))
    cheval = repos["course"].create_cheval(Cheval(nom="Cheval Test"))
    partant = repos["course"].create_partant(Partant(course_id=course.id, cheval_id=cheval.id, numero=1))
    repos["course"].create_cote(Cote(partant_id=partant.id, operateur="PMU", cote=3.0))

    client.post("/api/v1/administration/automatisations/analyse-jour")
    reponse = client.post("/api/v1/administration/automatisations/analyse-jour")

    assert reponse.status_code == 200
    corps = reponse.json()["data"]
    assert corps["nb_courses"] == 1
    assert corps["nb_deja_parties"] == 0
    assert corps["nb_erreurs"] == 0
    taches = repos["tache"].lister(categorie="automatisation")
    assert taches[0].statut == "succes"
    analyses = repos["analyse"].list_analyses_by_course(course.id)
    assert sorted(a.version for a in analyses) == [1, 2]


def test_declencher_analyse_jour_ignore_les_courses_deja_parties(client, repos):
    reunion = repos["course"].create_reunion(Reunion(date=date.today(), hippodrome_id=1, numero=1))
    repos["course"].create_course(
        Course(reunion_id=reunion.id, numero=1, nom="Course déjà partie", heure_depart=datetime.now() - timedelta(hours=1))
    )

    reponse = client.post("/api/v1/administration/automatisations/analyse-jour")

    assert reponse.status_code == 200
    corps = reponse.json()["data"]
    assert corps["nb_courses"] == 0
    assert corps["nb_deja_parties"] == 1
    assert corps["nb_erreurs"] == 0


def test_declencher_recuperation_gains_calcule_et_journalise(client, repos):
    repos["controle_roi"].controles = [ControleRoi(analyse_id=1, mise=10.0, gains=15.0, profit=5.0, roi=50.0, valide=True)]

    reponse = client.post("/api/v1/administration/automatisations/gains")

    assert reponse.status_code == 200
    assert reponse.json()["data"] == {"nb_controles_roi": 1}
    taches = repos["tache"].lister(categorie="automatisation")
    assert any(t.nom == "recuperation_gains" and t.statut == "succes" for t in taches)


def test_declencher_statistiques_recalcule_et_journalise(client, repos):
    repos["statistiques"].a_calculer_globale = StatistiqueGlobale(nb_courses=0, nb_jouees=0)

    reponse = client.post("/api/v1/administration/automatisations/statistiques")

    assert reponse.status_code == 200
    taches = repos["tache"].lister(categorie="automatisation")
    assert any(t.nom == "calcul_statistiques" and t.statut == "succes" for t in taches)


# -- Rejeu (moteur de backtesting, L031.7 §4) --------------------------------------

# cf. tests/fixtures/reference_analyse_non_regression.json — même scénario figé
# (partant n°1 = Base, score le plus haut) : réutilisé ici pour un rejeu réel.
_RAPPORTS_PARTANT_1_GAGNANT = [
    {"typePari": "SIMPLE_GAGNANT", "rembourse": False, "rapports": [{"combinaison": "1", "dividendePourUnEuro": 140}]},
    {"typePari": "SIMPLE_PLACE", "rembourse": False, "rapports": [{"combinaison": "1", "dividendePourUnEuro": 130}]},
]


def _preparer_course_rejouable(course_repo, jour=date(2026, 1, 1)):
    reunion = course_repo.create_reunion(Reunion(date=jour, hippodrome_id=1, numero=1))
    course = course_repo.create_course(Course(reunion_id=reunion.id, numero=1, nom="Course Test Rejeu"))
    partants_config = [("Cheval Alpha", 2.5, "1p2p1p", 1), ("Cheval Beta", 4.0, "3p4p2p", 2), ("Cheval Gamma", 12.0, "7p8p9p", 3)]
    dernier_partant = None
    for nom, cote, musique, numero in partants_config:
        cheval = course_repo.create_cheval(Cheval(nom=nom))
        partant = course_repo.create_partant(
            Partant(course_id=course.id, cheval_id=cheval.id, numero=numero, musique=musique)
        )
        course_repo.create_cote(Cote(partant_id=partant.id, operateur="PMU", cote=cote))
        dernier_partant = partant
    course_repo.get_or_create_resultat(Resultat(course_id=course.id, partant_id=dernier_partant.id, classement=3))
    return course


def test_declencher_rejeu_recalcule_et_journalise(client, repos):
    course = _preparer_course_rejouable(repos["course"])
    repos["pmu_rejeu"].rapports_par_course[(1, 1)] = _RAPPORTS_PARTANT_1_GAGNANT

    reponse = client.post(
        "/api/v1/administration/rejeu",
        json={
            "version_modele": "test-rejeu",
            "date_debut": "2026-01-01",
            "date_fin": "2026-01-01",
            "commentaire": "Test intégration",
        },
    )

    assert reponse.status_code == 200
    corps = reponse.json()["data"]
    assert corps["version_modele"] == "test-rejeu"
    assert corps["source"] == "rejeu"
    assert corps["nb_courses"] == 1
    assert corps["roi"] is not None
    assert corps["cree_le"] is not None

    taches = repos["tache"].lister(categorie="rejeu")
    assert any(t.nom == "rejeu_versions" and t.statut == "succes" for t in taches)


def test_declencher_rejeu_sans_courses_eligibles_renvoie_zero(client, repos):
    reponse = client.post(
        "/api/v1/administration/rejeu",
        json={"version_modele": "vide", "date_debut": "2020-01-01", "date_fin": "2020-01-02"},
    )

    assert reponse.status_code == 200
    corps = reponse.json()["data"]
    assert corps["nb_courses"] == 0
    assert corps["source"] == "rejeu"


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

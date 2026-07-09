"""Tests d'intégration de l'audit systématique des écritures — cf. plan "Audit
systématique des écritures". Utilise le client par défaut (utilisateur
Administrateur fictif, cf. tests/integration/conftest.py) sauf pour le test de
rôle sur GET /audit.
"""

import json

from api.dependencies.auth import get_utilisateur_courant
from api.main import app
from src.models.utilisateur import Role, Utilisateur


def test_creation_reunion_est_auditee(client, repos):
    reponse = client.post("/api/v1/reunions", json={"date": "2026-07-07", "hippodrome_id": 1, "numero": 1})
    reunion = reponse.json()["data"]

    entree = repos["audit"].entrees[-1]
    assert entree.action == "creation_reunion"
    assert entree.objet == str(reunion["id"])
    assert entree.ancien_etat is None
    assert json.loads(entree.nouvel_etat)["id"] == reunion["id"]


def test_modification_reunion_est_auditee_avec_ancien_et_nouvel_etat(client, repos):
    reunion = client.post(
        "/api/v1/reunions", json={"date": "2026-07-07", "hippodrome_id": 1, "numero": 1}
    ).json()["data"]

    client.patch(f"/api/v1/reunions/{reunion['id']}", json={"statut": "Terminée"})

    entree = repos["audit"].entrees[-1]
    assert entree.action == "modification_reunion"
    assert entree.objet == str(reunion["id"])
    assert json.loads(entree.ancien_etat)["statut"] != "Terminée"
    assert json.loads(entree.nouvel_etat)["statut"] == "Terminée"


def test_suppression_reunion_est_auditee_avec_ancien_etat_seul(client, repos):
    reunion = client.post(
        "/api/v1/reunions", json={"date": "2026-07-07", "hippodrome_id": 1, "numero": 1}
    ).json()["data"]

    client.delete(f"/api/v1/reunions/{reunion['id']}")

    entree = repos["audit"].entrees[-1]
    assert entree.action == "suppression_reunion"
    assert entree.objet == str(reunion["id"])
    assert json.loads(entree.ancien_etat)["id"] == reunion["id"]
    assert entree.nouvel_etat is None


def test_patch_reunion_inconnue_ne_cree_aucun_audit(client, repos):
    nb_avant = len(repos["audit"].entrees)
    client.patch("/api/v1/reunions/999", json={"statut": "Terminée"})
    assert len(repos["audit"].entrees) == nb_avant


def test_declenchement_analyse_est_audite(client, repos):
    reunion = client.post(
        "/api/v1/reunions", json={"date": "2026-07-07", "hippodrome_id": 1, "numero": 1}
    ).json()["data"]
    course = client.post(
        f"/api/v1/reunions/{reunion['id']}/courses", json={"numero": 1, "nom": "Prix Test"}
    ).json()["data"]

    reponse = client.post(
        f"/api/v1/courses/{course['id']}/analyses",
        json={
            "version": 1,
            "partants": [{"partant_id": 1, "sous_scores": {"marche": 80.0, "presse": 70.0}, "cote": 3.0}],
            "sous_risques_course": {"marche": 30, "presse": 20},
        },
    )
    analyse = reponse.json()["data"]["analyse"]

    entree = repos["audit"].entrees[-1]
    assert entree.action == "declenchement_analyse"
    assert entree.objet == str(analyse["id"])


def test_get_audit_accessible_a_administrateur(client, repos):
    client.post("/api/v1/reunions", json={"date": "2026-07-07", "hippodrome_id": 1, "numero": 1})
    reponse = client.get("/api/v1/audit")
    assert reponse.status_code == 200
    assert len(reponse.json()["data"]) >= 1


def test_get_audit_refuse_role_non_administrateur(client):
    role_analyste = Role(id=2, nom="Analyste")
    utilisateur_analyste = Utilisateur(id=2, login="analyste", mot_de_passe="", role_id=2)
    app.dependency_overrides[get_utilisateur_courant] = lambda: (utilisateur_analyste, role_analyste)

    reponse = client.get("/api/v1/audit")
    assert reponse.status_code == 403

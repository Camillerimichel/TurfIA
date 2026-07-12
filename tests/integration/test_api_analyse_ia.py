"""Tests d'intégration de l'endpoint POST /courses/{id}/analyses/ia — analyse IA à
la demande (Claude Sonnet 5, cf. IaAnalyseService), alimente les familles de score
"value"/"contexte" jamais calculées par aucune autre voie.
"""

from src.core.exceptions import AnalysisError


def _creer_course_avec_partants(client, cotes_et_musiques):
    reunion = client.post(
        "/api/v1/reunions", json={"date": "2026-07-07", "hippodrome_id": 1, "numero": 1}
    ).json()["data"]
    course = client.post(
        f"/api/v1/reunions/{reunion['id']}/courses", json={"numero": 1, "nom": "Prix Test IA"}
    ).json()["data"]

    for i, (nom, cote, musique) in enumerate(cotes_et_musiques, start=1):
        cheval = client.post("/api/v1/chevaux", json={"nom": nom, "musique": musique}).json()["data"]
        client.post(
            f"/api/v1/courses/{course['id']}/partants",
            json={"cheval_id": cheval["id"], "numero": i},
        )

    return course


def test_analyse_ia_persiste_source_ia_et_synthese(client, repos):
    course = _creer_course_avec_partants(
        client,
        [("Cheval A", 3.5, "1p2p1p"), ("Cheval B", 8.0, "9p0p8p")],
    )
    partants = repos["course"].list_partants_by_course(course["id"])
    for partant, cote in zip(partants, [3.5, 8.0]):
        repos["course"].cotes[partant.id] = cote
    repos["ia"].synthese = "Le favori sort d'une bonne série et semble sous-coté."

    reponse = client.post(f"/api/v1/courses/{course['id']}/analyses/ia", json={})
    assert reponse.status_code == 201
    detail = reponse.json()["data"]
    assert detail["analyse"]["source"] == "ia"
    assert detail["analyse"]["commentaire"] == "Le favori sort d'une bonne série et semble sous-coté."
    # L'IA a bien reçu le contexte des 2 partants (pas moins que le moteur classique).
    assert len(repos["ia"].appels) == 1
    _contexte_course, contextes_partants = repos["ia"].appels[0]
    assert {p.partant_id for p in contextes_partants} == {p.id for p in partants}


def test_analyse_ia_echec_ne_persiste_rien(client, repos):
    course = _creer_course_avec_partants(client, [("Cheval A", 3.5, "1p2p1p")])
    partants = repos["course"].list_partants_by_course(course["id"])
    repos["course"].cotes[partants[0].id] = 3.5
    repos["ia"].echec = AnalysisError("Analyse IA impossible : limite de requêtes Anthropic atteinte.")

    reponse = client.post(f"/api/v1/courses/{course['id']}/analyses/ia", json={})
    assert reponse.status_code == 422
    assert reponse.json()["success"] is False
    assert repos["analyse"].list_analyses_by_course(course["id"]) == []


def test_analyse_ia_course_inconnue_retourne_404(client):
    reponse = client.post("/api/v1/courses/999/analyses/ia", json={})
    assert reponse.status_code == 404

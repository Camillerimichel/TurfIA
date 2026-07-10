"""Tests d'intégration de l'endpoint POST /courses/{id}/analyses/auto — referme la
boucle collecte -> analyse (cf. PreparationDonneesService), sans saisie manuelle.
"""


def _creer_course_avec_partants(client, cotes_et_musiques):
    reunion = client.post(
        "/api/v1/reunions", json={"date": "2026-07-07", "hippodrome_id": 1, "numero": 1}
    ).json()["data"]
    course = client.post(
        f"/api/v1/reunions/{reunion['id']}/courses", json={"numero": 1, "nom": "Prix Test Auto"}
    ).json()["data"]

    for i, (nom, cote, musique) in enumerate(cotes_et_musiques, start=1):
        cheval = client.post("/api/v1/chevaux", json={"nom": nom, "musique": musique}).json()["data"]
        client.post(
            f"/api/v1/courses/{course['id']}/partants",
            json={"cheval_id": cheval["id"], "numero": i},
        )

    return course


def test_analyse_auto_calcule_les_sous_scores_depuis_les_donnees_collectees(client, repos):
    course = _creer_course_avec_partants(
        client,
        [("Cheval A", 3.5, "1p2p1p"), ("Cheval B", 8.0, "9p0p8p"), ("Cheval C", 5.0, "5p4p3p")],
    )
    # Simule des cotes déjà collectées (cf. CollecteService en conditions réelles) :
    partants = repos["course"].list_partants_by_course(course["id"])
    cotes = [3.5, 8.0, 5.0]
    for partant, cote in zip(partants, cotes):
        repos["course"].cotes[partant.id] = cote

    reponse = client.post(f"/api/v1/courses/{course['id']}/analyses/auto", json={})
    assert reponse.status_code == 201
    detail = reponse.json()["data"]
    assert detail["analyse"]["course_id"] == course["id"]
    assert len(detail["partants"]) == 3
    # Le partant avec la meilleure cote (favori) ET la meilleure forme doit être en tête.
    tete = next(p for p in detail["partants"] if p["rang"] == 1)
    assert tete["partant_id"] == partants[0].id


def test_analyse_auto_sans_cote_collectee_retourne_422(client):
    course = _creer_course_avec_partants(client, [("Cheval Sans Cote", None, None)])
    reponse = client.post(f"/api/v1/courses/{course['id']}/analyses/auto", json={})
    assert reponse.status_code == 422
    assert reponse.json()["success"] is False


def test_analyse_auto_course_inconnue_retourne_404(client):
    reponse = client.post("/api/v1/courses/999/analyses/auto", json={})
    assert reponse.status_code == 404


def test_analyse_auto_meme_version_retourne_409(client, repos):
    course = _creer_course_avec_partants(client, [("Cheval A", 3.5, "1p2p1p")])
    partants = repos["course"].list_partants_by_course(course["id"])
    repos["course"].cotes[partants[0].id] = 3.5

    premiere = client.post(f"/api/v1/courses/{course['id']}/analyses/auto", json={"version": 1})
    assert premiere.status_code == 201

    deuxieme = client.post(f"/api/v1/courses/{course['id']}/analyses/auto", json={"version": 1})
    assert deuxieme.status_code == 409


def test_analyse_auto_version_suivante_permet_de_relancer_quand_on_veut(client, repos):
    """Verrou de non-régression pour le déclenchement manuel « à volonté »
    (cf. html/static/js/course.js) : viser la version suivante plutôt que de
    rejouer la même doit toujours réussir, même après une analyse déjà
    existante (ex. automatisation horaire en version 1)."""
    course = _creer_course_avec_partants(client, [("Cheval A", 3.5, "1p2p1p")])
    partants = repos["course"].list_partants_by_course(course["id"])
    repos["course"].cotes[partants[0].id] = 3.5

    premiere = client.post(f"/api/v1/courses/{course['id']}/analyses/auto", json={"version": 1})
    assert premiere.status_code == 201

    deuxieme = client.post(f"/api/v1/courses/{course['id']}/analyses/auto", json={"version": 2})
    assert deuxieme.status_code == 201
    assert deuxieme.json()["data"]["analyse"]["version"] == 2

"""Tests d'intégration de l'endpoint POST /courses/{id}/analyses/auto — referme la
boucle collecte -> analyse (cf. PreparationDonneesService), sans saisie manuelle.
"""


def _creer_course_avec_partants(client, cotes_et_musiques, quinte=False):
    reunion = client.post(
        "/api/v1/reunions", json={"date": "2026-07-07", "hippodrome_id": 1, "numero": 1}
    ).json()["data"]
    course = client.post(
        f"/api/v1/reunions/{reunion['id']}/courses",
        json={"numero": 1, "nom": "Prix Test Auto", "quinte": quinte},
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


def _creer_course_base_et_chance(client, quinte):
    """Cotes + musique choisies (au niveau du partant, pas seulement du
    cheval — cf. `PreparationDonneesService`, la famille "forme" lit
    `Partant.musique`) pour obtenir de façon fiable 1 Base + 1 Chance
    régulière, condition nécessaire à "Couplé Placé"."""
    reunion = client.post(
        "/api/v1/reunions", json={"date": "2026-07-07", "hippodrome_id": 1, "numero": 1}
    ).json()["data"]
    course = client.post(
        f"/api/v1/reunions/{reunion['id']}/courses",
        json={"numero": 1, "nom": "Prix Test Auto Quinté", "quinte": quinte},
    ).json()["data"]

    for i, (nom, cote, musique) in enumerate(
        [("Cheval A", 2.5, "1p1p1p"), ("Cheval B", 4.0, "1p2p1p"), ("Cheval C", 15.0, "9p9p9p")], start=1
    ):
        cheval = client.post("/api/v1/chevaux", json={"nom": nom, "musique": musique}).json()["data"]
        client.post(
            f"/api/v1/courses/{course['id']}/partants",
            json={"cheval_id": cheval["id"], "numero": i, "musique": musique},
        )
    return course


def test_analyse_auto_propage_quinte_de_la_course(client, repos):
    """Retour utilisateur (2026-07-13, structure de paris spécifique aux
    courses Quinté+) : `/auto` doit propager `course.quinte` jusqu'à
    `construire_paris` — Couplé Placé (ici constructible : 1 Base + 1 Chance
    régulière) ne doit apparaître que si la course est réellement Quinté+."""
    course_ordinaire = _creer_course_base_et_chance(client, quinte=False)
    partants = repos["course"].list_partants_by_course(course_ordinaire["id"])
    for partant, cote in zip(partants, [2.5, 4.0, 15.0]):
        repos["course"].cotes[partant.id] = cote
    reponse_ordinaire = client.post(f"/api/v1/courses/{course_ordinaire['id']}/analyses/auto", json={})
    assert reponse_ordinaire.status_code == 201
    types_ordinaire = {p["type_pari"] for p in reponse_ordinaire.json()["data"]["paris"]}
    assert "Couplé Placé" not in types_ordinaire

    course_quinte = _creer_course_base_et_chance(client, quinte=True)
    partants_quinte = repos["course"].list_partants_by_course(course_quinte["id"])
    for partant, cote in zip(partants_quinte, [2.5, 4.0, 15.0]):
        repos["course"].cotes[partant.id] = cote
    reponse_quinte = client.post(f"/api/v1/courses/{course_quinte['id']}/analyses/auto", json={})
    assert reponse_quinte.status_code == 201
    types_quinte = {p["type_pari"] for p in reponse_quinte.json()["data"]["paris"]}
    assert "Couplé Placé" in types_quinte


def test_analyse_auto_vise_toujours_la_version_suivante(client, repos):
    """Verrou de non-régression pour le déclenchement manuel « à volonté »
    (cf. html/static/js/course.js) : `analyses/auto` ignore tout `version`
    fourni et vise systématiquement la version suivante (cf. AnalyseService.
    prochaine_version) — jamais de conflit, même après une analyse déjà
    existante (ex. automatisation horaire)."""
    course = _creer_course_avec_partants(client, [("Cheval A", 3.5, "1p2p1p")])
    partants = repos["course"].list_partants_by_course(course["id"])
    repos["course"].cotes[partants[0].id] = 3.5

    premiere = client.post(f"/api/v1/courses/{course['id']}/analyses/auto", json={})
    assert premiere.status_code == 201
    assert premiere.json()["data"]["analyse"]["version"] == 1

    deuxieme = client.post(f"/api/v1/courses/{course['id']}/analyses/auto", json={})
    assert deuxieme.status_code == 201
    assert deuxieme.json()["data"]["analyse"]["version"] == 2

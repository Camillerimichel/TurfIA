"""Tests d'intégration de POST /courses/{id}/analyses/{analyse_id}/selectionner —
fige manuellement quelle analyse compte pour l'historique/ROI d'une course, au lieu
du calcul automatique MAX(version) (retour utilisateur, 2026-07-12).
"""


def _creer_course_avec_deux_versions(client, repos):
    reunion = client.post(
        "/api/v1/reunions", json={"date": "2026-07-07", "hippodrome_id": 1, "numero": 1}
    ).json()["data"]
    course = client.post(
        f"/api/v1/reunions/{reunion['id']}/courses", json={"numero": 1, "nom": "Prix Test Sélection"}
    ).json()["data"]
    cheval = client.post("/api/v1/chevaux", json={"nom": "Cheval A", "musique": "1p2p1p"}).json()["data"]
    client.post(f"/api/v1/courses/{course['id']}/partants", json={"cheval_id": cheval["id"], "numero": 1})
    partants = repos["course"].list_partants_by_course(course["id"])
    repos["course"].cotes[partants[0].id] = 3.5

    premiere = client.post(f"/api/v1/courses/{course['id']}/analyses/auto", json={}).json()["data"]
    deuxieme = client.post(f"/api/v1/courses/{course['id']}/analyses/auto", json={}).json()["data"]
    return course, premiere["analyse"], deuxieme["analyse"]


def test_selectionner_une_ancienne_version_bascule_le_flag(client, repos):
    course, premiere, deuxieme = _creer_course_avec_deux_versions(client, repos)

    # Par défaut (aucune sélection manuelle) : la dernière version est "selectionnee".
    liste = client.get(f"/api/v1/courses/{course['id']}/analyses").json()["data"]
    assert {a["id"]: a["selectionnee"] for a in liste} == {premiere["id"]: False, deuxieme["id"]: True}

    reponse = client.post(f"/api/v1/courses/{course['id']}/analyses/{premiere['id']}/selectionner")
    assert reponse.status_code == 200
    resultat = reponse.json()["data"]
    assert {a["id"]: a["selectionnee"] for a in resultat} == {premiere["id"]: True, deuxieme["id"]: False}

    # La sélection persiste sur un GET suivant, pas seulement dans la réponse du POST.
    liste_apres = client.get(f"/api/v1/courses/{course['id']}/analyses").json()["data"]
    assert {a["id"]: a["selectionnee"] for a in liste_apres} == {premiere["id"]: True, deuxieme["id"]: False}


def test_selectionner_analyse_dune_autre_course_retourne_404(client, repos):
    course_1, premiere, _ = _creer_course_avec_deux_versions(client, repos)
    course_2, _, _ = _creer_course_avec_deux_versions(client, repos)

    reponse = client.post(f"/api/v1/courses/{course_2['id']}/analyses/{premiere['id']}/selectionner")
    assert reponse.status_code == 404


def test_selectionner_analyse_inconnue_retourne_404(client, repos):
    course, _, _ = _creer_course_avec_deux_versions(client, repos)
    reponse = client.post(f"/api/v1/courses/{course['id']}/analyses/999999/selectionner")
    assert reponse.status_code == 404


def test_selectionner_course_inconnue_retourne_404(client):
    reponse = client.post("/api/v1/courses/999/analyses/1/selectionner")
    assert reponse.status_code == 404


def test_selectionner_declenche_le_controle_roi_manquant(client, repos):
    course, premiere, _ = _creer_course_avec_deux_versions(client, repos)

    reponse = client.post(f"/api/v1/courses/{course['id']}/analyses/{premiere['id']}/selectionner")
    assert reponse.status_code == 200
    assert repos["controle_roi"].analyses_controlees == [premiere["id"]]

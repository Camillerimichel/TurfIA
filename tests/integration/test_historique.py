"""Tests d'intégration du module Historique (L018 §8) — recherche transversale
en lecture seule, sans base réelle (cf. tests/integration/fakes.py)."""

from datetime import datetime, timedelta

from src.models.analyse import ControleRoi, ControleRoiPari


def _creer_course_avec_analyse_et_pari(client, decision="Jeu normal", version=1):
    reunion = client.post(
        "/api/v1/reunions", json={"date": "2026-07-07", "hippodrome_id": 1, "numero": 1}
    ).json()["data"]
    course = client.post(
        f"/api/v1/reunions/{reunion['id']}/courses", json={"numero": 1, "nom": "Prix Test"}
    ).json()["data"]
    cheval = client.post("/api/v1/chevaux", json={"nom": "Cheval Test"}).json()["data"]
    partant = client.post(
        f"/api/v1/courses/{course['id']}/partants", json={"cheval_id": cheval["id"], "numero": 1}
    ).json()["data"]

    detail = client.post(
        f"/api/v1/courses/{course['id']}/analyses",
        json={
            "version": version,
            "partants": [{"partant_id": partant["id"], "sous_scores": {"marche": 90}, "cote": 3.0}],
            "sous_risques_course": {"marche": 20},
            "mise_reference": 10,
        },
    ).json()["data"]
    return reunion, course, detail


def _creer_course_avec_heure(client, reunion_id, numero, nom, heure_depart):
    course = client.post(
        f"/api/v1/reunions/{reunion_id}/courses",
        json={"numero": numero, "nom": nom, "heure_depart": heure_depart},
    ).json()["data"]
    cheval = client.post("/api/v1/chevaux", json={"nom": f"Cheval {nom}"}).json()["data"]
    partant = client.post(
        f"/api/v1/courses/{course['id']}/partants", json={"cheval_id": cheval["id"], "numero": 1}
    ).json()["data"]
    client.post(
        f"/api/v1/courses/{course['id']}/analyses",
        json={
            "version": 1,
            "partants": [{"partant_id": partant["id"], "sous_scores": {"marche": 90}, "cote": 3.0}],
            "sous_risques_course": {"marche": 20},
            "mise_reference": 10,
        },
    )
    return course


def test_historique_trie_date_recente_dabord_puis_heures_croissantes(client):
    """Retour utilisateur (2026-07-12, correction du tri initial) : « il faut
    mettre la dernière date en premier et mettre les courses par ordre
    chronologique sur les heures/minutes » — la date la plus récente
    d'abord, puis à l'intérieur d'une même date les courses du matin avant
    celles du soir (pas l'inverse)."""
    reunion_recente = client.post(
        "/api/v1/reunions", json={"date": "2026-07-08", "hippodrome_id": 1, "numero": 1}
    ).json()["data"]
    reunion_ancienne = client.post(
        "/api/v1/reunions", json={"date": "2026-07-07", "hippodrome_id": 1, "numero": 2}
    ).json()["data"]

    course_recente_tard = _creer_course_avec_heure(
        client, reunion_recente["id"], 2, "Récente Tard", "2026-07-08T18:00:00"
    )
    course_recente_tot = _creer_course_avec_heure(
        client, reunion_recente["id"], 1, "Récente Tôt", "2026-07-08T09:00:00"
    )
    course_ancienne = _creer_course_avec_heure(client, reunion_ancienne["id"], 1, "Ancienne", "2026-07-07T12:00:00")

    reponse = client.get("/api/v1/historique")

    assert reponse.status_code == 200
    ids_dans_lordre = [l["course_id"] for l in reponse.json()["data"]]
    ids_suivis = (course_recente_tard["id"], course_recente_tot["id"], course_ancienne["id"])
    ordre_filtre = [cid for cid in ids_dans_lordre if cid in ids_suivis]
    # Une course peut produire plusieurs lignes (un pari chacune) : on ne
    # vérifie que l'ordre relatif des courses, pas le nombre de lignes.
    ordre_courses = [cid for i, cid in enumerate(ordre_filtre) if i == 0 or cid != ordre_filtre[i - 1]]
    # Date la plus récente (2026-07-08) d'abord, et à l'intérieur de cette
    # date la course du matin (9h) avant celle du soir (18h) — puis la date
    # la plus ancienne (2026-07-07).
    assert ordre_courses == [course_recente_tot["id"], course_recente_tard["id"], course_ancienne["id"]]


def test_historique_sans_filtre_retourne_les_lignes(client):
    reunion, course, detail = _creer_course_avec_analyse_et_pari(client)

    reponse = client.get("/api/v1/historique")

    assert reponse.status_code == 200
    lignes = reponse.json()["data"]
    assert len(lignes) >= 1
    ligne = next(l for l in lignes if l["analyse_id"] == detail["analyse"]["id"])
    assert ligne["course_id"] == course["id"]
    assert ligne["hippodrome_id"] == reunion["hippodrome_id"]
    assert ligne["date_calcul"] == detail["analyse"]["date_calcul"]


def test_historique_expose_le_gain_reel_du_controle_roi(client, repos):
    """retour utilisateur : « dans historique, dans le tableau de résultat,
    ajoute le gain en euros » — `gains_reel` (montant brut réellement gagné,
    distinct du profit net) doit venir de `controle_roi_pari.gains`."""
    _, _, detail = _creer_course_avec_analyse_et_pari(client)
    pari_id = repos["analyse"].list_paris_by_analyse(detail["analyse"]["id"])[0].id
    repos["analyse"].create_controle_roi_pari(
        ControleRoiPari(pari_id=pari_id, mise=10.0, gains=15.0, profit=5.0, roi=50.0, valide=True)
    )

    reponse = client.get("/api/v1/historique")

    assert reponse.status_code == 200
    ligne = next(l for l in reponse.json()["data"] if l["analyse_id"] == detail["analyse"]["id"])
    assert ligne["gains_reel"] == 15.0
    assert ligne["profit_reel"] == 5.0


def test_historique_filtre_par_hippodrome_inconnu_est_vide(client):
    _creer_course_avec_analyse_et_pari(client)

    reponse = client.get("/api/v1/historique", params={"hippodrome_id": 999})

    assert reponse.status_code == 200
    assert reponse.json()["data"] == []


def test_historique_filtre_par_date(client):
    _creer_course_avec_analyse_et_pari(client)

    reponse = client.get("/api/v1/historique", params={"date_debut": "2026-01-01", "date_fin": "2026-01-31"})

    assert reponse.status_code == 200
    assert reponse.json()["data"] == []


def test_historique_filtre_par_type_pari(client):
    _, _, detail = _creer_course_avec_analyse_et_pari(client)
    type_pari_attendu = detail["paris"][0]["type_pari"] if detail["paris"] else None

    reponse = client.get("/api/v1/historique", params={"type_pari": "Type inexistant"})
    assert reponse.json()["data"] == []

    if type_pari_attendu is not None:
        reponse = client.get("/api/v1/historique", params={"type_pari": type_pari_attendu})
        assert len(reponse.json()["data"]) >= 1


def test_historique_ne_montre_que_la_derniere_version_par_course(client):
    """Non-régression : une course réanalysée plusieurs fois (cf. L033,
    automatisation horaire à version croissante) ne doit apparaître qu'une
    seule fois dans l'historique, avec la version la plus récente — pas une
    ligne par version calculée dans la journée."""
    reunion, course, detail_v1 = _creer_course_avec_analyse_et_pari(client, version=1)
    partant_id = int(detail_v1["paris"][0]["combinaison"]) if detail_v1["paris"] else None
    reponse_v2 = client.post(
        f"/api/v1/courses/{course['id']}/analyses",
        json={
            "version": 2,
            "partants": [{"partant_id": partant_id, "sous_scores": {"marche": 90}, "cote": 3.0}],
            "sous_risques_course": {"marche": 20},
            "mise_reference": 10,
        },
    )
    assert reponse_v2.status_code == 201
    detail_v2 = reponse_v2.json()["data"]

    reponse = client.get("/api/v1/historique")

    assert reponse.status_code == 200
    lignes = [l for l in reponse.json()["data"] if l["course_id"] == course["id"]]
    assert len(lignes) >= 1
    # Toutes les lignes de cette course viennent de la même (dernière) analyse —
    # peu importe qu'elle ait plusieurs paris (plusieurs lignes légitimes),
    # jamais un mélange de versions différentes.
    assert {l["analyse_id"] for l in lignes} == {detail_v2["analyse"]["id"]}
    assert {l["version"] for l in lignes} == {2}


def test_historique_reflete_la_selection_manuelle(client):
    """Non-régression (retour utilisateur, 2026-07-12) : sélectionner
    manuellement une ancienne version d'analyse pour une course doit faire
    remonter CETTE version dans l'historique, pas systématiquement la
    dernière (cf. `POST .../analyses/{id}/selectionner`)."""
    reunion, course, detail_v1 = _creer_course_avec_analyse_et_pari(client, version=1)
    partant_id = int(detail_v1["paris"][0]["combinaison"]) if detail_v1["paris"] else None
    client.post(
        f"/api/v1/courses/{course['id']}/analyses",
        json={
            "version": 2,
            "partants": [{"partant_id": partant_id, "sous_scores": {"marche": 90}, "cote": 3.0}],
            "sous_risques_course": {"marche": 20},
            "mise_reference": 10,
        },
    )

    selection = client.post(f"/api/v1/courses/{course['id']}/analyses/{detail_v1['analyse']['id']}/selectionner")
    assert selection.status_code == 200

    reponse = client.get("/api/v1/historique")
    lignes = [l for l in reponse.json()["data"] if l["course_id"] == course["id"]]
    assert {l["analyse_id"] for l in lignes} == {detail_v1["analyse"]["id"]}
    assert {l["version"] for l in lignes} == {1}


def _creer_reunion_et_course(client, heure_depart=None, numero_reunion=1):
    reunion = client.post(
        "/api/v1/reunions", json={"date": "2026-07-07", "hippodrome_id": 1, "numero": numero_reunion}
    ).json()["data"]
    corps_course = {"numero": 1, "nom": "Prix Test"}
    if heure_depart is not None:
        corps_course["heure_depart"] = heure_depart
    course = client.post(f"/api/v1/reunions/{reunion['id']}/courses", json=corps_course).json()["data"]
    return reunion, course


def test_paris_en_cours_liste_une_course_a_venir_a_budget_engage(client):
    """cf. page Accueil, bloc ROI global — retour utilisateur : liste des paris
    à surveiller avant leur course, avec lien vers la fiche course."""
    reunion, course = _creer_reunion_et_course(client)
    cheval = client.post("/api/v1/chevaux", json={"nom": "Cheval Test"}).json()["data"]
    partant = client.post(
        f"/api/v1/courses/{course['id']}/partants", json={"cheval_id": cheval["id"], "numero": 1}
    ).json()["data"]
    detail = client.post(
        f"/api/v1/courses/{course['id']}/analyses",
        json={
            "version": 1,
            "partants": [{"partant_id": partant["id"], "sous_scores": {"marche": 90}, "cote": 3.0}],
            "sous_risques_course": {"marche": 20},
            "mise_reference": 10,
        },
    ).json()["data"]
    assert detail["analyse"]["budget"] > 0

    reponse = client.get("/api/v1/historique/paris-en-cours")

    assert reponse.status_code == 200
    lignes = reponse.json()["data"]
    ligne = next(l for l in lignes if l["course_id"] == course["id"])
    assert ligne["analyse_id"] == detail["analyse"]["id"]
    assert ligne["budget"] == detail["analyse"]["budget"]
    assert ligne["hippodrome_nom"]


def test_paris_en_cours_exclut_les_courses_deja_parties(client):
    reunion, course = _creer_reunion_et_course(client, heure_depart="2020-01-01T12:00:00")
    cheval = client.post("/api/v1/chevaux", json={"nom": "Cheval Test"}).json()["data"]
    partant = client.post(
        f"/api/v1/courses/{course['id']}/partants", json={"cheval_id": cheval["id"], "numero": 1}
    ).json()["data"]
    detail = client.post(
        f"/api/v1/courses/{course['id']}/analyses",
        json={
            "version": 1,
            "partants": [{"partant_id": partant["id"], "sous_scores": {"marche": 90}, "cote": 3.0}],
            "sous_risques_course": {"marche": 20},
            "mise_reference": 10,
        },
    ).json()["data"]
    assert detail["analyse"]["budget"] > 0

    reponse = client.get("/api/v1/historique/paris-en-cours")

    assert reponse.status_code == 200
    assert all(l["course_id"] != course["id"] for l in reponse.json()["data"])


def test_paris_en_cours_exclut_quand_aucun_budget_engage(client):
    """Décision « Ne pas jouer » (score < 60, cf. L031.1 §9) -> budget 0 (cf.
    PALIERS_BUDGET_PAR_DEFAUT) : rien à surveiller, la course est exclue."""
    reunion, course = _creer_reunion_et_course(client)
    cheval = client.post("/api/v1/chevaux", json={"nom": "Cheval Test"}).json()["data"]
    partant = client.post(
        f"/api/v1/courses/{course['id']}/partants", json={"cheval_id": cheval["id"], "numero": 1}
    ).json()["data"]
    detail = client.post(
        f"/api/v1/courses/{course['id']}/analyses",
        json={
            "version": 1,
            "partants": [{"partant_id": partant["id"], "sous_scores": {"marche": 10}, "cote": 3.0}],
            "sous_risques_course": {"marche": 80},
            "mise_reference": 10,
        },
    ).json()["data"]
    assert detail["analyse"]["decision"] == "Ne pas jouer"
    assert detail["analyse"]["budget"] == 0

    reponse = client.get("/api/v1/historique/paris-en-cours")

    assert reponse.status_code == 200
    assert all(l["course_id"] != course["id"] for l in reponse.json()["data"])


def test_paris_en_cours_ne_montre_que_la_derniere_version(client):
    reunion, course, detail_v1 = _creer_course_avec_analyse_et_pari(client, version=1)
    partant_id = int(detail_v1["paris"][0]["combinaison"])
    reponse_v2 = client.post(
        f"/api/v1/courses/{course['id']}/analyses",
        json={
            "version": 2,
            "partants": [{"partant_id": partant_id, "sous_scores": {"marche": 90}, "cote": 3.0}],
            "sous_risques_course": {"marche": 20},
            "mise_reference": 10,
        },
    )
    detail_v2 = reponse_v2.json()["data"]

    reponse = client.get("/api/v1/historique/paris-en-cours")

    assert reponse.status_code == 200
    lignes = [l for l in reponse.json()["data"] if l["course_id"] == course["id"]]
    assert len(lignes) == 1
    assert lignes[0]["analyse_id"] == detail_v2["analyse"]["id"]


def test_historique_filtre_decisions_ou_logique(client):
    """cf. accueil.js : un filtre à choix multiples est une condition "ou"."""
    _, course_normal, detail = _creer_course_avec_analyse_et_pari(client)
    decision_reelle = detail["analyse"]["decision"]

    reponse = client.get("/api/v1/historique", params={"decisions": [decision_reelle, "Décision inexistante"]})
    assert reponse.status_code == 200
    assert any(l["course_id"] == course_normal["id"] for l in reponse.json()["data"])

    reponse_vide = client.get("/api/v1/historique", params={"decisions": ["Décision inexistante"]})
    assert reponse_vide.json()["data"] == []


# -- Gains récents (Accueil) --------------------------------------------------
# Retour utilisateur : « il faut implémenter la récupération des gains,
# attention à ne pas générer de doublons » — vérifie que la liste ne montre
# qu'une course arrivée avec un gain déjà connu, jamais un doublon.


def _creer_course_arrivee_avec_analyse(client, repos, heure_depart, mise=10.0, gains=15.0):
    reunion, course = _creer_reunion_et_course(client, heure_depart=heure_depart.isoformat())
    cheval = client.post("/api/v1/chevaux", json={"nom": "Cheval Test"}).json()["data"]
    partant = client.post(
        f"/api/v1/courses/{course['id']}/partants", json={"cheval_id": cheval["id"], "numero": 1}
    ).json()["data"]
    detail = client.post(
        f"/api/v1/courses/{course['id']}/analyses",
        json={
            "version": 1,
            "partants": [{"partant_id": partant["id"], "sous_scores": {"marche": 90}, "cote": 3.0}],
            "sous_risques_course": {"marche": 20},
            "mise_reference": 10,
        },
    ).json()["data"]
    analyse_id = detail["analyse"]["id"]
    repos["analyse"].create_controle_roi(
        ControleRoi(analyse_id=analyse_id, mise=mise, gains=gains, profit=gains - mise, roi=50.0, valide=True)
    )
    return course, detail


def test_gains_recents_liste_une_course_arrivee_avec_controle_roi(client, repos):
    heure_depart = datetime.now() - timedelta(hours=2)
    course, detail = _creer_course_arrivee_avec_analyse(client, repos, heure_depart)

    reponse = client.get("/api/v1/historique/gains-recents")

    assert reponse.status_code == 200
    lignes = reponse.json()["data"]
    ligne = next(l for l in lignes if l["course_id"] == course["id"])
    assert ligne["analyse_id"] == detail["analyse"]["id"]
    assert ligne["mise"] == 10.0
    assert ligne["gains"] == 15.0
    assert ligne["valide"] is True
    # Une seule ligne par course, jamais de doublon.
    assert len([l for l in lignes if l["course_id"] == course["id"]]) == 1


def test_gains_recents_exclut_les_courses_sans_controle_roi(client):
    heure_depart = datetime.now() - timedelta(hours=2)
    reunion, course = _creer_reunion_et_course(client, heure_depart=heure_depart.isoformat())
    cheval = client.post("/api/v1/chevaux", json={"nom": "Cheval Test"}).json()["data"]
    partant = client.post(
        f"/api/v1/courses/{course['id']}/partants", json={"cheval_id": cheval["id"], "numero": 1}
    ).json()["data"]
    client.post(
        f"/api/v1/courses/{course['id']}/analyses",
        json={
            "version": 1,
            "partants": [{"partant_id": partant["id"], "sous_scores": {"marche": 90}, "cote": 3.0}],
            "sous_risques_course": {"marche": 20},
            "mise_reference": 10,
        },
    )

    reponse = client.get("/api/v1/historique/gains-recents")

    assert reponse.status_code == 200
    assert all(l["course_id"] != course["id"] for l in reponse.json()["data"])


def test_gains_recents_exclut_hors_fenetre(client, repos):
    heure_depart = datetime.now() - timedelta(hours=48)
    course, _ = _creer_course_arrivee_avec_analyse(client, repos, heure_depart)

    reponse = client.get("/api/v1/historique/gains-recents")

    assert reponse.status_code == 200
    assert all(l["course_id"] != course["id"] for l in reponse.json()["data"])

    reponse_large = client.get("/api/v1/historique/gains-recents", params={"heures": 72})
    assert any(l["course_id"] == course["id"] for l in reponse_large.json()["data"])

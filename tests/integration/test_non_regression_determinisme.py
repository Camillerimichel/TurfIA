"""Suite de non-régression par déterminisme — cf. L020 §8.3 et L006 ADR-001
(déterminisme du moteur) : rejoue un scénario figé à travers l'intégralité du
moteur d'analyse (PreparationDonneesService -> AnalyseService, pondérations
par défaut) et compare le résultat aux valeurs de référence enregistrées dans
`tests/fixtures/reference_analyse_non_regression.json`.

Tout écart, même minime, est un échec de test — jamais un ajustement
silencieux du fichier de référence. Si un écart est un changement
intentionnel (nouvelle version de règles, cf. L009 §5.1), régénérer le
fichier de référence explicitement (relancer le scénario ci-dessous,
comparer le diff, documenter la raison dans le commit) plutôt que de
mettre à jour la valeur sans revue.

Scénario délibérément simple (3 partants, sans jockey/entraineur/consensus
presse/conditions de piste connues — familles Professionnels/Presse/Aptitude
absentes) pour rester facile à relire ; le but n'est pas de couvrir toutes
les familles (déjà fait ailleurs) mais de figer le comportement bout-en-bout.
"""

import json
from datetime import date
from pathlib import Path

import pytest

from src.models.course import Cheval, Cote, Course, Partant, Reunion
from src.models.statistique import StatistiqueHippodrome
from src.services.analyse_service import AnalyseService
from src.services.preparation_service import PreparationDonneesService
from tests.integration.fakes import FakeAnalyseRepository, FakeCourseRepository, FakeStatistiqueRepository

FIXTURES = Path(__file__).parent.parent / "fixtures"

# (nom du cheval, cote directe, musique) — figé, ne jamais modifier sans
# régénérer la référence.
_PARTANTS_FIGES = [
    ("Cheval Alpha", 2.5, "1p2p1p"),
    ("Cheval Beta", 4.0, "3p4p2p"),
    ("Cheval Gamma", 12.0, "7p8p9p"),
]


def _rejouer_scenario_fige():
    course_repo = FakeCourseRepository()
    statistique_repo = FakeStatistiqueRepository()

    reunion = course_repo.create_reunion(Reunion(date=date(2026, 1, 1), hippodrome_id=1, numero=1))
    course = course_repo.create_course(Course(reunion_id=reunion.id, numero=1, nom="Course Test Non-Régression"))

    numero_par_partant_id: dict[int, int] = {}
    for numero, (nom, cote, musique) in enumerate(_PARTANTS_FIGES, start=1):
        cheval = course_repo.create_cheval(Cheval(nom=nom))
        # `musique` sur le Partant (pas le Cheval) : reflète l'historique du
        # cheval tel que connu pour CETTE course précise (cf. PMU, corrigé le
        # 2026-07-10 dans PreparationDonneesService — cf. PROJECT_STATE.md).
        partant = course_repo.create_partant(
            Partant(course_id=course.id, cheval_id=cheval.id, numero=numero, musique=musique)
        )
        course_repo.create_cote(Cote(partant_id=partant.id, operateur="PMU", cote=cote))
        numero_par_partant_id[partant.id] = numero

    # ROI/nb_courses figés du moteur à cet hippodrome (famille Historique, cf.
    # calculer_indicateur_historique_moteur) — identique pour les 3 partants.
    statistique_repo.create_hippodrome(
        StatistiqueHippodrome(hippodrome_id=1, nb_courses=5, mises=1000.0, gains=1150.0, profit=150.0, roi=15.0)
    )

    preparation = PreparationDonneesService(course_repo, statistique_repo)
    donnees_partants, sous_risques_course = preparation.preparer_donnees_partants(course.id)

    # Pondérations par défaut (aucune personnalisation) : c'est le comportement
    # réel du moteur en production, pas un rejeu avec des poids custom.
    service = AnalyseService(FakeAnalyseRepository())
    resultat = service.analyser_course(
        course_id=course.id,
        version=1,
        partants=donnees_partants,
        sous_risques_course=sous_risques_course,
        persister=False,
    )
    return resultat, numero_par_partant_id


def _serialiser(resultat, numero_par_partant_id: dict[int, int]) -> dict:
    partants_par_numero = {}
    for pc in resultat.partants_classes:
        numero = numero_par_partant_id[pc.partant_id]
        partants_par_numero[str(numero)] = {
            "rang": pc.rang,
            "score_turfia": pc.score_turfia,
            "score_final": pc.score_final,
            "categorie": pc.categorie,
            "value_bet": pc.value_bet,
            "roi_theorique": pc.roi_theorique,
        }

    paris = []
    for pari in resultat.paris:
        numeros = sorted(numero_par_partant_id[int(pid)] for pid in pari.combinaison.split("-"))
        paris.append(
            {"type_pari": pari.type_pari, "numeros": numeros, "mise": pari.mise, "roi_estime": pari.roi_estime}
        )

    return {
        "analyse": {
            "score_confiance": resultat.analyse.score_confiance,
            "risque": resultat.analyse.risque,
            "roi_theorique": resultat.analyse.roi_theorique,
            "decision": resultat.analyse.decision,
            "budget": resultat.analyse.budget,
        },
        "partants_par_numero": partants_par_numero,
        "paris": paris,
    }


def _comparer_recursivement(actuel, reference, chemin: str = ""):
    if isinstance(reference, dict):
        assert isinstance(actuel, dict), f"{chemin} : dict attendu, obtenu {type(actuel)}"
        for cle in reference:
            _comparer_recursivement(actuel.get(cle), reference[cle], f"{chemin}.{cle}")
    elif isinstance(reference, list):
        assert isinstance(actuel, list), f"{chemin} : liste attendue, obtenue {type(actuel)}"
        assert len(actuel) == len(reference), f"{chemin} : {len(actuel)} élément(s), {len(reference)} attendu(s)"
        for i, (a, r) in enumerate(zip(actuel, reference)):
            _comparer_recursivement(a, r, f"{chemin}[{i}]")
    elif isinstance(reference, float):
        assert actuel == pytest.approx(reference, abs=1e-9), f"{chemin} : {actuel} != {reference} (référence)"
    else:
        assert actuel == reference, f"{chemin} : {actuel!r} != {reference!r} (référence)"


def test_analyse_bout_en_bout_reste_identique_a_la_reference_figee():
    reference = json.loads(
        (FIXTURES / "reference_analyse_non_regression.json").read_text(encoding="utf-8")
    )
    reference.pop("_note", None)

    resultat, numero_par_partant_id = _rejouer_scenario_fige()
    actuel = _serialiser(resultat, numero_par_partant_id)

    _comparer_recursivement(actuel, reference)

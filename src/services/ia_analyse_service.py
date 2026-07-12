"""Analyse IA à la demande (Claude Sonnet 5, API Anthropic) — cf. retour
utilisateur du 2026-07-12 : alimente enfin les familles de score "value" et
"contexte", définies depuis toujours dans `PONDERATIONS_PAR_DEFAUT` (cf.
`src.algorithms.score`) mais jamais calculées par aucun code existant.

Purement à la demande, pour une course sélectionnée à la fois (pas
d'automatisation/planification, cf. décision explicite). Échec net et sans
persistance partielle en cas de problème (réseau, refus, réponse malformée) —
même principe "pas de score fabriqué" que `PreparationDonneesService`.
"""

from __future__ import annotations

import json
from dataclasses import dataclass

import anthropic

from src.core.exceptions import AnalysisError

MODELE_IA = "claude-sonnet-5"

_SCHEMA_SORTIE = {
    "type": "object",
    "properties": {
        "partants": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "partant_id": {"type": "integer"},
                    "value": {"type": "number"},
                    "contexte": {"type": "number"},
                },
                "required": ["partant_id", "value", "contexte"],
                "additionalProperties": False,
            },
        },
        "synthese": {"type": "string"},
    },
    "required": ["partants", "synthese"],
    "additionalProperties": False,
}


@dataclass
class ContextePartantIa:
    """Signal déjà disponible pour un partant, transmis à l'IA — les mêmes
    données que le moteur classique (cf. `CourseRepository.
    list_partants_detail_by_course`), pas moins."""

    partant_id: int
    numero: int
    cheval_nom: str
    cote: float | None
    musique: str | None
    jockey_nom: str | None
    entraineur_nom: str | None
    sous_scores: dict[str, float]


@dataclass
class ContexteCourseIa:
    hippodrome_nom: str
    discipline: str | None
    distance_metres: int | None
    allocation: float | None
    terrain: str | None


@dataclass
class ResultatIa:
    scores_par_partant: dict[int, tuple[float, float]]
    synthese: str


class IaAnalyseService:
    def __init__(self, client: anthropic.Anthropic | None = None) -> None:
        self._client = client if client is not None else anthropic.Anthropic()

    def analyser(self, course: ContexteCourseIa, partants: list[ContextePartantIa]) -> ResultatIa:
        prompt = self._construire_prompt(course, partants)
        try:
            reponse = self._client.messages.create(
                model=MODELE_IA,
                max_tokens=8192,
                output_config={"format": {"type": "json_schema", "schema": _SCHEMA_SORTIE}},
                messages=[{"role": "user", "content": prompt}],
            )
        except anthropic.APIConnectionError as exc:
            raise AnalysisError("Analyse IA impossible : l'API Anthropic est injoignable (réseau).") from exc
        except anthropic.RateLimitError as exc:
            raise AnalysisError(
                "Analyse IA impossible : limite de requêtes Anthropic atteinte, réessayez plus tard."
            ) from exc
        except anthropic.APIStatusError as exc:
            raise AnalysisError(f"Analyse IA impossible : erreur de l'API Anthropic ({exc.status_code}).") from exc

        if reponse.stop_reason == "refusal":
            raise AnalysisError("Analyse IA refusée par Claude (contenu jugé sensible).")
        texte = next((bloc.text for bloc in reponse.content if bloc.type == "text"), None)
        if texte is None:
            raise AnalysisError("Analyse IA impossible : réponse vide (aucun bloc texte).")
        try:
            donnees = json.loads(texte)
        except json.JSONDecodeError as exc:
            raise AnalysisError("Analyse IA impossible : réponse JSON invalide.") from exc
        return self._valider_et_convertir(donnees, {p.partant_id for p in partants})

    def _valider_et_convertir(self, donnees: dict, ids_attendus: set[int]) -> ResultatIa:
        partants_bruts = donnees.get("partants")
        synthese = donnees.get("synthese")
        if not isinstance(partants_bruts, list) or not isinstance(synthese, str) or not synthese.strip():
            raise AnalysisError("Analyse IA impossible : structure de réponse inattendue.")

        scores: dict[int, tuple[float, float]] = {}
        for item in partants_bruts:
            try:
                partant_id = int(item["partant_id"])
                valeur = float(item["value"])
                contexte = float(item["contexte"])
            except (KeyError, TypeError, ValueError) as exc:
                raise AnalysisError(f"Analyse IA impossible : entrée partant malformée ({item!r}).") from exc
            if not (0 <= valeur <= 100) or not (0 <= contexte <= 100):
                raise AnalysisError(f"Analyse IA impossible : score hors de [0, 100] pour le partant {partant_id}.")
            scores[partant_id] = (valeur, contexte)

        manquants = ids_attendus - scores.keys()
        if manquants:
            raise AnalysisError(f"Analyse IA impossible : partant(s) {sorted(manquants)} sans score value/contexte.")
        return ResultatIa(scores_par_partant=scores, synthese=synthese.strip())

    def _construire_prompt(self, course: ContexteCourseIa, partants: list[ContextePartantIa]) -> str:
        lignes = [
            "Tu es un analyste hippique expérimenté. Analyse la course suivante et "
            "note, pour CHAQUE partant listé ci-dessous, deux scores de 0 à 100 :",
            "- « value » : le cheval est-il sous-coté (valeur au regard de sa cote "
            "actuelle et des indicateurs déjà calculés) ? 100 = très sous-coté "
            "(bonne valeur), 0 = surcoté.",
            "- « contexte » : dans quelle mesure le contexte élargi de la course "
            "(distance, terrain, discipline, forme récente via la musique, écurie) "
            "joue en faveur de ce cheval ? 100 = contexte très favorable, 0 = très "
            "défavorable.",
            "",
            "Contexte de la course :",
            f"- Hippodrome : {course.hippodrome_nom}",
            f"- Discipline : {course.discipline or 'inconnue'}",
            f"- Distance : {course.distance_metres or 'inconnue'} m" if course.distance_metres else "- Distance : inconnue",
            f"- État du terrain : {course.terrain or 'inconnu'}",
            f"- Allocation : {course.allocation if course.allocation is not None else 'inconnue'} €",
            "",
            "Partants (numéro, cheval, cote actuelle, musique, jockey, entraîneur, "
            "sous-scores déjà calculés par le moteur classique de TurfIA — même "
            "signal, à toi d'ajouter value/contexte) :",
        ]
        for p in partants:
            sous_scores_texte = ", ".join(f"{cle}={valeur:.1f}" for cle, valeur in sorted(p.sous_scores.items()))
            lignes.append(
                f"- partant_id={p.partant_id} | N°{p.numero} {p.cheval_nom} | "
                f"cote={p.cote if p.cote is not None else 'n/a'} | "
                f"musique={p.musique or 'n/a'} | jockey={p.jockey_nom or 'n/a'} | "
                f"entraîneur={p.entraineur_nom or 'n/a'} | sous-scores : {sous_scores_texte or 'aucun'}"
            )
        lignes += [
            "",
            "Réponds avec un score value et un score contexte pour CHAQUE partant "
            "listé (utilise exactement les partant_id ci-dessus), et rédige une "
            "synthèse courte en français (quelques phrases) expliquant les points "
            "clés de ton analyse pour cette course.",
        ]
        return "\n".join(lignes)

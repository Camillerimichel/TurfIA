"""Schémas du domaine Analyses — cf. L007 §4.3, L030.3, L031.x.

`AnalyseDetailOut` sert à la fois de réponse au déclenchement d'une analyse (§10.1) et
à sa relecture (`GET /analyses/{id}`) : même forme quelle que soit l'origine des
données (calcul immédiat ou relecture depuis la base).
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DonneesPartantIn(BaseModel):
    partant_id: int
    sous_scores: dict[str, float]
    cote: float = Field(gt=0)
    consensus: float = 50.0
    evolution_cote: float = 0.0


class AnalyseTriggerIn(BaseModel):
    version: int = 1
    partants: list[DonneesPartantIn]
    sous_risques_course: dict[str, float]
    mise_reference: float = 10.0
    budget_precedent: float = 0.0
    perte_precedente: bool = False


class AnalyseAutoIn(BaseModel):
    """Déclenchement automatique : les sous-scores et le risque sont calculés à
    partir des données déjà collectées (cf. PreparationDonneesService), seuls les
    paramètres de mise/budget restent à la discrétion de l'appelant. Pas de champ
    `version` : toujours la version suivante (cf. AnalyseService.prochaine_version),
    pour pouvoir relancer une analyse à tout moment sans jamais entrer en conflit
    avec une version déjà calculée (cf. PROJECT_STATE.md).
    """

    mise_reference: float = 10.0
    budget_precedent: float = 0.0
    perte_precedente: bool = False


class AnalyseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    course_id: int
    version: int
    date_calcul: datetime | None = None
    score_confiance: float | None = None
    risque: float | None = None
    roi_theorique: float | None = None
    decision: str | None = None
    budget: float
    commentaire: str | None = None
    source: str = "manuel"
    # Calculé côté requête (analyse_repository.get_analyse_selectionnee_id),
    # jamais une colonne de `analyses` — assigné après `model_validate()`
    # dans les routes qui en ont besoin (liste + sélection, cf. L018 §6-7).
    selectionnee: bool = False


class AnalysePartantOut(BaseModel):
    """Reflet de la table `analyse_partant` (cf. L030.3 §4) — `score` est le Score
    TurfIA brut, `confiance` est le score final après bonus/malus (cf. L031.6 §3).
    `numero`/`cheval_nom` sont joints à l'affichage (cf. `CourseRepository.
    list_partants_detail_by_course`) : `partant_id` seul est un identifiant
    technique, pas un numéro de course exploitable pour parier réellement.
    """

    model_config = ConfigDict(from_attributes=True)

    partant_id: int
    numero: int | None = None
    cheval_nom: str | None = None
    score: float | None = None
    rang: int | None = None
    consensus: float | None = None
    evolution_cote: float | None = None
    value_bet: bool
    confiance: float | None = None
    categorie: str | None = None


class ParisOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    type_pari: str
    combinaison: str | None = None
    combinaison_lisible: str | None = None
    # Un Quinté Flexi couvre plusieurs combinaisons de 5 chevaux à la fois (cf.
    # L031.6 §5) : `sous_combinaisons` les liste individuellement (une par
    # ticket réellement joué), `mise_par_combinaison` répartit la mise totale
    # entre elles. `None` pour tout autre type de pari (une seule combinaison).
    sous_combinaisons: list[str] | None = None
    mise_par_combinaison: float | None = None
    mise: float
    gain_estime: float | None = None
    roi_estime: float | None = None


class AnalyseDetailOut(BaseModel):
    analyse: AnalyseOut
    partants: list[AnalysePartantOut]
    paris: list[ParisOut]

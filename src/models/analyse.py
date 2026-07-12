"""Modèles des tables d'analyse — cf. L030.3, L015 §5. Immuables après création."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Analyse:
    course_id: int
    version: int
    id: int | None = None
    date_calcul: datetime | None = None
    score_confiance: float | None = None
    risque: float | None = None
    roi_theorique: float | None = None
    decision: str | None = None
    budget: float = 0.0
    commentaire: str | None = None
    source: str = "manuel"


@dataclass(frozen=True)
class AnalysePartant:
    analyse_id: int
    partant_id: int
    id: int | None = None
    score: float | None = None
    rang: int | None = None
    consensus: float | None = None
    evolution_cote: float | None = None
    value_bet: bool = False
    confiance: float | None = None
    commentaire: str | None = None


@dataclass(frozen=True)
class Selection:
    analyse_id: int
    partant_id: int
    categorie: str
    id: int | None = None
    ordre_affichage: int | None = None


@dataclass(frozen=True)
class Pari:
    analyse_id: int
    type_pari: str
    id: int | None = None
    combinaison: str | None = None
    mise: float = 0.0
    gain_estime: float | None = None
    roi_estime: float | None = None


@dataclass(frozen=True)
class ControleRoi:
    analyse_id: int
    id: int | None = None
    mise: float = 0.0
    gains: float = 0.0
    profit: float | None = None
    roi: float | None = None
    valide: bool = False
    commentaire: str | None = None


@dataclass(frozen=True)
class ControleRoiPari:
    """Détail par pari du contrôle ROI (cf. L011 §8.7) — `controle_roi` reste
    l'agrégat par analyse ; cette table donne la granularité par pari nécessaire
    à `statistique_pari` depuis qu'une analyse produit plusieurs types de pari
    (cf. `src.algorithms.classement.construire_paris`)."""

    pari_id: int
    id: int | None = None
    mise: float = 0.0
    gains: float = 0.0
    profit: float | None = None
    roi: float | None = None
    valide: bool = False

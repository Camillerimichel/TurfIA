"""Service d'orchestration de l'analyse TurfIA — cf. L015 §7, L006 §3.

Enchaîne la chaîne de calcul documentée en L006 §3 et L031.1 §6 : validation minimale,
score par partant, risque de la course, value bets, classement, décision, budget, et
persistance des résultats. Aucun code HTTP ici (cf. L015 §7.2) : ce service est appelé
aussi bien par l'API que par les traitements planifiés (cf. ADR-002 de L033).

Simplification assumée pour cette première tranche (documentée pour rester honnête sur
le périmètre) : le score de confiance de la course est celui du partant classé en tête
après classement, et le ROI théorique de la course est celui de ce même partant. Une
agrégation plus fine (cf. L031.4 §7) pourra affiner ce point sans changer la signature
du service.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from src.algorithms.classement import (
    PartantClasse,
    calculer_budget,
    calculer_score_final,
    categoriser,
    construire_paris,
    trier_partants,
    verifier_absence_martingale,
)
from src.algorithms.risque import calculer_risque
from src.algorithms.roi_theorique import esperance, probabilite_turfia, probabilites_implicites_normalisees, roi_theorique
from src.algorithms.score import calculer_score, determiner_decision
from src.algorithms.value_bets import est_value_bet
from src.core.exceptions import ValidationError
from src.models.analyse import Analyse, AnalysePartant, Pari, Selection
from src.repositories.analyse_repository import AnalyseRepository


@dataclass
class DonneesPartant:
    """Indicateurs déjà calculés en amont (collecte/normalisation) pour un partant."""

    partant_id: int
    sous_scores: dict[str, float]
    cote: float
    consensus: float = 50.0
    evolution_cote: float = 0.0


@dataclass
class ResultatAnalyse:
    analyse: Analyse
    partants_classes: list[PartantClasse] = field(default_factory=list)
    selections: list[Selection] = field(default_factory=list)
    paris: list[Pari] = field(default_factory=list)


class AnalyseService:
    def __init__(
        self,
        analyse_repository: AnalyseRepository,
        poids_score: dict[str, float] | None = None,
        poids_risque: dict[str, float] | None = None,
    ) -> None:
        self._repo = analyse_repository
        self._poids_score = poids_score
        self._poids_risque = poids_risque

    def deja_analysee(self, course_id: int, version: int) -> bool:
        return self._repo.existe_analyse(course_id, version)

    def analyser_course(
        self,
        course_id: int,
        version: int,
        partants: list[DonneesPartant],
        sous_risques_course: dict[str, float],
        mise_reference: float = 10.0,
        budget_precedent: float = 0.0,
        perte_precedente: bool = False,
        persister: bool = True,
    ) -> ResultatAnalyse:
        if not partants:
            raise ValidationError("Une analyse nécessite au moins un partant.")

        # 1. Score TurfIA par partant (L031.2)
        scores = {p.partant_id: calculer_score(p.sous_scores, self._poids_score) for p in partants}
        somme_scores = sum(scores.values())

        # 2. Probabilités (L031.4)
        probabilites_marche = probabilites_implicites_normalisees([p.cote for p in partants])
        probabilites_par_partant = {
            p.partant_id: probabilite_turfia(scores[p.partant_id], somme_scores) for p in partants
        }

        # 3. Risque de la course (L031.3) — indépendant des chevaux
        risque_course = calculer_risque(sous_risques_course, self._poids_risque)

        # 4. Value bets (L031.5) et ROI par partant (L031.4)
        partants_classes: list[PartantClasse] = []
        rois_par_partant: dict[int, float] = {}
        for i, p in enumerate(partants):
            p_marche = probabilites_marche[i]
            p_turfia = probabilites_par_partant[p.partant_id]
            value_bet = est_value_bet(scores[p.partant_id], p_turfia, p_marche, risque_course)

            esperance_pari = esperance(p_turfia, rapport_estime=p.cote, mise=mise_reference)
            roi = roi_theorique(esperance_pari, mise_reference)
            rois_par_partant[p.partant_id] = roi

            score_final = calculer_score_final(scores[p.partant_id], value_bet, risque_course)
            partants_classes.append(
                PartantClasse(
                    partant_id=p.partant_id,
                    score_turfia=scores[p.partant_id],
                    score_final=score_final,
                    risque=risque_course,
                    roi_theorique=roi,
                    consensus=p.consensus,
                    evolution_cote=p.evolution_cote,
                    value_bet=value_bet,
                )
            )

        # 5. Classement et catégorisation (L031.6)
        partants_classes = trier_partants(partants_classes)
        for partant_classe in partants_classes:
            categoriser(partant_classe)

        tete_de_liste = partants_classes[0]
        score_confiance = tete_de_liste.score_final
        roi_course = tete_de_liste.roi_theorique

        # 6. Décision et budget (L031.1 §9, L031.6 §6) avec garde-fou anti-martingale
        decision = determiner_decision(score_confiance)
        budget = calculer_budget(score_confiance)
        verifier_absence_martingale(budget, budget_precedent, perte_precedente)

        analyse = Analyse(
            course_id=course_id,
            version=version,
            score_confiance=round(score_confiance, 2),
            risque=round(risque_course, 2),
            roi_theorique=round(roi_course, 2),
            decision=decision,
            budget=budget,
        )

        selections: list[Selection] = []

        if persister:
            analyse = self._repo.create_analyse(analyse)
            for partant_classe in partants_classes:
                self._repo.create_analyse_partant(
                    AnalysePartant(
                        analyse_id=analyse.id,
                        partant_id=partant_classe.partant_id,
                        score=round(partant_classe.score_turfia, 2),
                        rang=partant_classe.rang,
                        consensus=partant_classe.consensus,
                        evolution_cote=partant_classe.evolution_cote,
                        value_bet=partant_classe.value_bet,
                        confiance=round(partant_classe.score_final, 2),
                    )
                )
                selection = self._repo.create_selection(
                    Selection(
                        analyse_id=analyse.id,
                        partant_id=partant_classe.partant_id,
                        categorie=partant_classe.categorie,
                        ordre_affichage=partant_classe.rang,
                    )
                )
                selections.append(selection)

        # Toujours construits en mémoire (y compris `persister=False`, cf. moteur de
        # rejeu L031.7 §4 qui a besoin des paris sans les persister) ; seule leur
        # écriture en base est conditionnée par `persister`.
        paris: list[Pari] = []
        for type_pari, chevaux, mise in construire_paris(partants_classes, budget):
            roi_estime = sum(c.roi_theorique for c in chevaux) / len(chevaux)
            pari = Pari(
                analyse_id=analyse.id,
                type_pari=type_pari,
                combinaison="-".join(str(c.partant_id) for c in chevaux),
                mise=mise,
                roi_estime=round(roi_estime, 2),
            )
            if persister:
                pari = self._repo.create_pari(pari)
            paris.append(pari)

        return ResultatAnalyse(analyse=analyse, partants_classes=partants_classes, selections=selections, paris=paris)

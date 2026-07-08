"""Registre déclaratif des sources de données hippiques, organisées en 4 niveaux
(cf. plan de collecte validé) :

- Niveau 1 — Données officielles (vérité terrain)
- Niveau 2 — Marché (cotes)
- Niveau 3 — Consensus presse (agrégation de plusieurs pronostiqueurs)
- Niveau 4 — Base TurfIA propriétaire (déjà satisfait par le schéma existant,
  cf. L030.3/L030.4 ; non listé ici car ce n'est pas une source externe)

Ce registre documente la trajectoire multi-sources de façon exécutable plutôt que
dans un simple commentaire : `SOURCES_IMPLEMENTEES` peut être filtré à l'exécution
(cf. `CollecteService`), et toute tentative d'utiliser une source non implémentée
échoue explicitement plutôt que silencieusement.
"""

from __future__ import annotations

from src.collecte.base import SourceInfo

RAISON_NON_VERIFIEE = "Site non exploré/vérifié dans cette tranche (cf. plan de collecte)."
RAISON_PROTECTION_ANTIBOT = "Protection anti-bot constatée à la vérification (HTTP 403/429)."
RAISON_DIRECTIVE_ROBOTS_ANTHROPIC = (
    "robots.txt bloque explicitement le user-agent anthropic-ai (Disallow: /), séparément de la "
    "règle générale User-Agent: * — non exploré par choix, pas par indisponibilité technique."
)
RAISON_ROBOTS_CONTENU_BLOQUE = (
    "robots.txt (User-agent: *) interdit les pages de pronostics/partants elles-mêmes, "
    "indépendamment de toute protection anti-bot active."
)

SOURCES: tuple[SourceInfo, ...] = (
    # Niveau 1 — Données officielles (vérité terrain)
    SourceInfo("PMU", niveau=1, role="Programme officiel, partants, non-partants, arrivées, rapports", implementee=True),
    SourceInfo(
        "France Galop",
        niveau=1,
        role="Courses de plat et d'obstacles, conditions de course, terrain, engagements",
        implementee=False,
        raison_si_non_implementee=RAISON_NON_VERIFIEE,
    ),
    SourceInfo(
        "LeTROT",
        niveau=1,
        role="Programme du trot, informations officielles, résultats",
        implementee=False,
        raison_si_non_implementee=RAISON_PROTECTION_ANTIBOT,
    ),
    # Niveau 2 — Marché (cotes)
    SourceInfo("PMU", niveau=2, role="Cotes PMU (rapport direct)", implementee=True),
    SourceInfo("ZEbet", niveau=2, role="Cotes marché", implementee=False, raison_si_non_implementee=RAISON_NON_VERIFIEE),
    SourceInfo("Genybet", niveau=2, role="Cotes marché", implementee=False, raison_si_non_implementee=RAISON_NON_VERIFIEE),
    SourceInfo("Unibet", niveau=2, role="Cotes marché (si disponible)", implementee=False, raison_si_non_implementee=RAISON_NON_VERIFIEE),
    SourceInfo("Betclic", niveau=2, role="Cotes marché (si disponible)", implementee=False, raison_si_non_implementee=RAISON_NON_VERIFIEE),
    # Niveau 3 — Consensus presse
    SourceInfo(
        "Paris-Turf", niveau=3, role="Consensus presse, pronostics, dernières informations",
        implementee=False, raison_si_non_implementee=RAISON_DIRECTIVE_ROBOTS_ANTHROPIC,
    ),
    SourceInfo(
        "Geny", niveau=3, role="Pronostics, avis des journalistes, statistiques",
        implementee=False,
        raison_si_non_implementee=(
            RAISON_PROTECTION_ANTIBOT + " " + RAISON_ROBOTS_CONTENU_BLOQUE
            + " (Disallow: /PronosticsPMU*, /PartantsPMU*, /FicheCheval*, /FicheJockey*, /StatsPMU*, etc.)"
        ),
    ),
    SourceInfo(
        "Canalturf",
        niveau=3,
        role=(
            "Consensus presse multi-journaux (~14 titres) — Quinté+ du jour uniquement, "
            "cf. src/collecte/canalturf/"
        ),
        implementee=True,
    ),
    SourceInfo(
        "ZEturf", niveau=3, role="Pronostics, cotes, commentaires",
        implementee=False,
        raison_si_non_implementee=RAISON_ROBOTS_CONTENU_BLOQUE + " (Disallow: /partants/)",
    ),
    SourceInfo(
        "Zone-Turf",
        niveau=3,
        role=(
            "Consensus presse multi-journaux (7 titres) — Quinté+ du jour uniquement, "
            "combiné à Canalturf (cf. src/collecte/zoneturf/, src/services/consensus_presse_service.py). "
            "Source ajoutée hors de la taxonomie initiale, à la demande de l'utilisateur."
        ),
        implementee=True,
    ),
)


def sources_par_niveau(niveau: int) -> tuple[SourceInfo, ...]:
    return tuple(s for s in SOURCES if s.niveau == niveau)


def sources_implementees() -> tuple[SourceInfo, ...]:
    return tuple(s for s in SOURCES if s.implementee)

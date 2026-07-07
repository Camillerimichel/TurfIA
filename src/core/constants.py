"""Constantes structurelles — cf. L011 §4.8, L031.x.

Ne contient que des bornes structurelles du modèle de données, jamais une pondération
ou un seuil métier : ceux-ci sont paramétrables et vivent dans la table `parametre`
(cf. L006 ADR-002, L026 §3.3) — jamais codés en dur ici.
"""

SCORE_MIN = 0
SCORE_MAX = 100

RISQUE_MIN = 0
RISQUE_MAX = 100

CATEGORIES_SELECTION = ("Base", "Chance régulière", "Outsider", "Tocard", "Écarté")

TYPES_PARI = (
    "Simple Gagnant",
    "Simple Placé",
    "Couplé Gagnant",
    "Couplé Placé",
    "2 sur 4",
    "Quinté Flexi",
)

DECISIONS = ("Ne pas jouer", "Jeu prudent", "Jeu normal", "Forte opportunité")

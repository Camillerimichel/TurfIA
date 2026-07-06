# L006_ALGORITHMES_v2.0.md --- Partie 2/3

# 5. Orchestration des calculs

Le moteur exécute les traitements selon un ordre strict garantissant la
reproductibilité des résultats. Chaque étape consomme uniquement les
données produites par l'étape précédente.

``` mermaid
flowchart TD
VAL[Validation]
NORM[Normalisation]
MET[Calcul des métriques]
RULES[Règles métier]
SCORE[Score TurfIA]
REC[Recommandations]

VAL --> NORM
NORM --> MET
MET --> RULES
RULES --> SCORE
SCORE --> REC
```

# 6. Décisions d'architecture

## ADR-001 --- Déterminisme

Les calculs ne dépendent d'aucun état interne non persistant.

## ADR-002 --- Paramétrage

Les pondérations sont externalisées afin de permettre leur évolution
sans modifier le code.

## ADR-003 --- Versionnement

Chaque exécution est associée à une version des règles métier
garantissant la comparabilité historique.

# 7. Gestion des anomalies

Les erreurs détectées interrompent uniquement le calcul concerné. Les
informations de diagnostic sont journalisées afin de permettre une
reprise contrôlée.

*Fin de la partie 2/3.*

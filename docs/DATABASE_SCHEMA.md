# Schéma logique de la base TurfIA

## Tables principales
- races
- runners
- pre_analyses
- final_analyses
- results
- bets
- roi_history
- model_parameters
- sources

## Relations
- Une course possède plusieurs partants.
- Chaque course possède au plus une pré-analyse, une analyse finale et un résultat officiel.
- Les paris sont rattachés à une analyse.
- Les statistiques de ROI sont historisées.

## Principes
- Clés primaires techniques.
- Clés étrangères systématiques.
- Historique immuable.
- Aucune suppression des données métier.
- Traçabilité complète des calculs.
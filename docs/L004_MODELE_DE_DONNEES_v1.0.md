L004 — Modèle de données de TurfIA

## Objectif
Définir le modèle de données relationnel utilisé par TurfIA.

## Principes
- Historisation complète.
- Normalisation des données.
- Clés techniques immuables.
- Aucune donnée codée en dur.

## Tables principales
- courses
- partants
- cotes
- analyses
- paris
- resultats
- historiques
- statistiques
- taches_planifiees

## Relations
- Une course possède plusieurs partants.
- Un partant possède plusieurs relevés de cotes.
- Une analyse est rattachée à une course.
- Une course possède un résultat officiel.
- Les statistiques sont calculées à partir des historiques.

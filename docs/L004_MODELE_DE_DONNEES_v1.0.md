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

## Table courses
Clé primaire : course_id

## Table partants
Clé primaire : partant_id
Clé étrangère : course_id

## Table cotes
Clé primaire : cote_id
Clé étrangère : partant_id

Colonnes :
- date_releve
- source
- cote
- evolution
- consensus

## Table analyses
Clé primaire : analyse_id
Clés étrangères : course_id

Colonnes :
- type_analyse
- score_confiance
- niveau_risque
- roi_theorique
- classement
- bases
- outsiders
- tocard
- recommandations

## Table resultats
Clé primaire : resultat_id
Clé étrangère : course_id

Colonnes :
- arrivee_officielle
- rapports_pmu
- gains
- profit
- roi
- date_controle

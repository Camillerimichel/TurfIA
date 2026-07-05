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

Colonnes principales :
- course_id
- date_course
- hippodrome
- reunion
- numero_course
- nom_course
- discipline
- distance
- corde
- surface
- terrain
- allocation
- heure_depart
- statut

## Table partants
Clé primaire : partant_id

Clés étrangères :
- course_id -> courses.course_id

Colonnes principales :
- partant_id
- course_id
- numero
- cheval
- age
- sexe
- entraineur
- jockey_driver
- musique
- valeur
- corde
- poids
- ferrure
- score_turfia

## Relations
- Une course possède plusieurs partants.
- Un partant possède plusieurs relevés de cotes.
- Une analyse est rattachée à une course.
- Une course possède un résultat officiel.
- Les statistiques sont calculées à partir des historiques.
L105 — Table SQL `resultats`

## Objectif
Définir la structure de la table des résultats officiels et des performances des analyses.

## Clé primaire
- resultat_id BIGINT

## Clé étrangère
- course_id BIGINT REFERENCES courses(course_id)

## Colonnes principales
- arrivee_officielle JSON
- rapports_pmu JSON
- gains DECIMAL(12,2)
- mise DECIMAL(12,2)
- profit DECIMAL(12,2)
- roi DECIMAL(8,2)
- date_publication TIMESTAMP
- date_controle TIMESTAMP
- created_at TIMESTAMP

## Contraintes
- NOT NULL sur course_id et arrivee_officielle.
- Unicité sur course_id.

## Index
- idx_resultats_course
- idx_resultats_date_publication
- idx_resultats_roi
L106 — Table SQL `historiques`

## Objectif
Définir la structure de la table assurant la traçabilité complète des analyses et des décisions.

## Clé primaire
- historique_id BIGINT

## Clés étrangères
- analyse_id BIGINT REFERENCES analyses(analyse_id)
- course_id BIGINT REFERENCES courses(course_id)

## Colonnes principales
- version_modele VARCHAR(30)
- version_configuration VARCHAR(30)
- score_confiance SMALLINT
- decision VARCHAR(30)
- budget DECIMAL(12,2)
- gains DECIMAL(12,2)
- profit DECIMAL(12,2)
- roi DECIMAL(8,2)
- commentaire TEXT
- created_at TIMESTAMP

## Contraintes
- NOT NULL sur analyse_id, course_id, version_modele et score_confiance.
- Conservation immuable après validation.

## Index
- idx_historiques_course
- idx_historiques_analyse
- idx_historiques_version
- idx_historiques_created_at
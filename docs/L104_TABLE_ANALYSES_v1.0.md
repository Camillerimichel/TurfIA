L104 — Table SQL `analyses`

## Objectif
Définir la structure de la table centrale des analyses TurfIA.

## Clé primaire
- analyse_id BIGINT

## Clé étrangère
- course_id BIGINT REFERENCES courses(course_id)

## Colonnes principales
- type_analyse VARCHAR(20)
- version_modele VARCHAR(30)
- score_confiance SMALLINT
- niveau_risque VARCHAR(20)
- roi_theorique DECIMAL(8,2)
- classement JSON
- bases JSON
- outsiders JSON
- tocard JSON
- recommandations JSON
- parametres JSON
- created_at TIMESTAMP

## Contraintes
- NOT NULL sur course_id, type_analyse et score_confiance.
- Unicité sur (course_id, type_analyse, version_modele).

## Index
- idx_analyses_course
- idx_analyses_score
- idx_analyses_type
- idx_analyses_version
L101 — Table SQL `courses`

## Objectif
Définir la structure de la table `courses`.

## Clé primaire
- course_id BIGINT

## Colonnes principales
- date_course DATE
- hippodrome VARCHAR(100)
- reunion SMALLINT
- numero_course SMALLINT
- nom_course VARCHAR(255)
- discipline VARCHAR(30)
- distance INTEGER
- corde VARCHAR(20)
- surface VARCHAR(30)
- terrain VARCHAR(30)
- allocation DECIMAL(12,2)
- heure_depart TIMESTAMP
- statut VARCHAR(20)
- created_at TIMESTAMP
- updated_at TIMESTAMP

## Contraintes
- Unicité sur (date_course, reunion, numero_course).
- NOT NULL sur les colonnes obligatoires.

## Index
- idx_courses_date
- idx_courses_hippodrome
- idx_courses_statut
L102 — Table SQL `partants`

## Objectif
Définir la structure de la table `partants`.

## Clé primaire
- partant_id BIGINT

## Clé étrangère
- course_id BIGINT REFERENCES courses(course_id)

## Colonnes principales
- numero SMALLINT
- cheval VARCHAR(150)
- age SMALLINT
- sexe CHAR(1)
- entraineur VARCHAR(150)
- jockey_driver VARCHAR(150)
- musique VARCHAR(50)
- valeur DECIMAL(6,2)
- poids DECIMAL(5,2)
- corde SMALLINT
- ferrure VARCHAR(20)
- created_at TIMESTAMP
- updated_at TIMESTAMP

## Contraintes
- Unicité sur (course_id, numero).
- NOT NULL sur course_id, numero et cheval.

## Index
- idx_partants_course
- idx_partants_cheval
- idx_partants_entraineur
- idx_partants_jockey
L103 — Table SQL `cotes`

## Objectif
Définir la structure de la table historisant les cotes des partants.

## Clé primaire
- cote_id BIGINT

## Clé étrangère
- partant_id BIGINT REFERENCES partants(partant_id)

## Colonnes principales
- source VARCHAR(50)
- cote DECIMAL(8,2)
- evolution DECIMAL(8,2)
- consensus BOOLEAN
- date_releve TIMESTAMP
- created_at TIMESTAMP

## Contraintes
- NOT NULL sur partant_id, source, cote et date_releve.
- Unicité sur (partant_id, source, date_releve).

## Index
- idx_cotes_partant
- idx_cotes_source
- idx_cotes_date_releve
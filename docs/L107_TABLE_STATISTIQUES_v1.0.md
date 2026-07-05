L107 — Table SQL `statistiques`

## Objectif
Définir la structure de la table des indicateurs agrégés de performance de TurfIA.

## Clé primaire
- statistique_id BIGINT

## Colonnes principales
- periode DATE
- nb_courses INTEGER
- nb_courses_jouees INTEGER
- nb_courses_ignorees INTEGER
- taux_reussite DECIMAL(5,2)
- gains DECIMAL(12,2)
- pertes DECIMAL(12,2)
- profit DECIMAL(12,2)
- roi_global DECIMAL(8,2)
- roi_confiance_faible DECIMAL(8,2)
- roi_confiance_moyenne DECIMAL(8,2)
- roi_confiance_forte DECIMAL(8,2)
- roi_simple DECIMAL(8,2)
- roi_couple DECIMAL(8,2)
- roi_deux_sur_quatre DECIMAL(8,2)
- roi_quinte_flexi DECIMAL(8,2)
- created_at TIMESTAMP

## Contraintes
- Unicité sur periode.
- NOT NULL sur periode et roi_global.

## Index
- idx_statistiques_periode
- idx_statistiques_roi
- idx_statistiques_reussite
L004 — Modèle de données de TurfIA

## Objectif
Définir le modèle de données relationnel utilisé par TurfIA.

## Principes
- Historisation complète.
- Normalisation des données.
- Clés techniques immuables.
- Aucune donnée codée en dur.

## Tables
courses, partants, cotes, analyses, resultats, historiques, statistiques, paris, taches_planifiees.

## Table historiques
PK : historique_id
FK : course_id, analyse_id
Colonnes : date_operation, version_analyse, score_confiance, mise, gains, profit, roi.

## Table statistiques
PK : statistique_id
Colonnes : periode, nb_courses, nb_jouees, taux_reussite, gains_cumules, pertes_cumulees, roi_global, roi_par_confiance.

## Table paris
PK : pari_id
FK : analyse_id
Colonnes : type_pari, selection, mise, gain, resultat.

## Table taches_planifiees
PK : tache_id
Colonnes : procedure, frequence, derniere_execution, prochaine_execution, statut.

## Contraintes
- Historisation sans suppression des analyses.
- Intégrité référentielle sur toutes les clés étrangères.
- Horodatage systématique des enregistrements.
- Index sur course_id, partant_id, date_course et score_confiance.
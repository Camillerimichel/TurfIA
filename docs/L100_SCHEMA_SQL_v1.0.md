L100 — Schéma SQL

## Objectif
Définir les conventions de conception de la base de données relationnelle de TurfIA.

## Principes
- Clés primaires techniques.
- Clés étrangères avec intégrité référentielle.
- Horodatage de tous les enregistrements.
- Historisation sans suppression logique des données de référence.

## Domaines fonctionnels
- Référentiel des courses.
- Référentiel des partants.
- Données de marché.
- Analyses TurfIA.
- Paris et résultats.
- Historique et statistiques.
- Configuration.

## Conventions
- Noms de tables au pluriel.
- Clés primaires suffixées par _id.
- Dates au format UTC.
- Index sur les colonnes de recherche fréquentes.
- Contraintes d'unicité sur les identifiants métier.

## Migrations
- Une migration par évolution.
- Migrations réversibles.
- Versionnement du schéma.
- Validation automatique avant déploiement.
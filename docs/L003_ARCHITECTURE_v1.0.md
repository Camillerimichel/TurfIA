L003 — Architecture générale de TurfIA

## Objectif

Décrire l'architecture fonctionnelle et technique de TurfIA.

## Principes d'architecture

- Séparation stricte des responsabilités.
- Modularité.
- Traçabilité.
- Reproductibilité.
- Aucune donnée codée en dur.
- Évolution incrémentale.
- Automatisation.

## Vue d'ensemble

Sources de données
→ Collecte
→ Normalisation / Validation
→ Base SQL
→ Moteur IA / Règles métier / Historique
→ Génération des analyses
→ API / Exports / Interface

## Architecture fonctionnelle

### Module Collecte
- Acquisition des données hippiques.
- Actualisation des cotes.
- Contrôle de cohérence.

### Module Normalisation
- Validation des données.
- Uniformisation des formats.
- Gestion des données manquantes.

### Module Analyse
- Calcul des scores TurfIA.
- Évaluation du risque.
- Calcul du ROI théorique.
- Classement des partants.

### Module Historique
- Archivage des analyses.
- Suivi des résultats.
- Calcul des statistiques.
- Amélioration continue.

## Architecture technique

- Base de données SQL.
- API REST interne.
- Moteur de règles métier.
- Moteur de scoring TurfIA.
- Service d'automatisation des procédures quotidiennes.
- Journalisation et traçabilité des traitements.
- Interfaces d'export (JSON, CSV, PDF).
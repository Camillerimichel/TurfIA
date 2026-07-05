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

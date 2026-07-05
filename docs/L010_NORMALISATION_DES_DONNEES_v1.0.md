L010 — Normalisation des données

## Objectif
Définir les règles de transformation des données collectées avant leur utilisation par le moteur TurfIA.

## Étapes de normalisation
1. Validation des formats.
2. Standardisation des unités et libellés.
3. Suppression des doublons.
4. Gestion des valeurs manquantes.
5. Contrôle de cohérence inter-sources.
6. Enrichissement par calcul des indicateurs dérivés.

## Principes
- Les données brutes restent inchangées.
- Toutes les transformations sont historisées.
- Chaque enregistrement conserve la référence de sa source.
- Les règles de normalisation sont versionnées.
- Les anomalies sont consignées dans un journal de traitement.
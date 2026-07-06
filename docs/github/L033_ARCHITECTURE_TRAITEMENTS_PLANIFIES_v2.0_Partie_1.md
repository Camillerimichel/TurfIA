# L033_ARCHITECTURE_TRAITEMENTS_PLANIFIES_v2.0 --- Partie 1/2

## 1. Objet

Ce document décrit l'architecture logicielle des traitements planifiés
de TurfIA. Il définit les composants responsables de l'exécution
automatique des traitements, leur séquencement, leurs dépendances, les
mécanismes de reprise sur incident, les règles de traçabilité et les
exigences de performance.

## 2. Périmètre

Les traitements planifiés couvrent l'ensemble des opérations
automatiques ne nécessitant aucune intervention utilisateur :

-   préparation quotidienne des analyses ;
-   récupération des données externes ;
-   calcul des scores ;
-   génération des recommandations ;
-   mise à jour des historiques ;
-   contrôle des résultats ;
-   calcul des indicateurs statistiques ;
-   maintenance technique.

## 3. Principes d'architecture

L'architecture repose sur les principes suivants :

-   indépendance des traitements ;
-   idempotence ;
-   journalisation complète ;
-   reprise automatique après incident ;
-   absence de dépendance circulaire ;
-   exécution déterministe.

## 4. Catégories de traitements

### 4.1 Collecte

Ces traitements interrogent les différentes sources de données afin de
récupérer les informations nécessaires aux analyses.

### 4.2 Préparation

Ils normalisent les données, vérifient leur cohérence et alimentent les
tables de travail.

### 4.3 Calcul

Ils exécutent les algorithmes TurfIA afin de produire les scores,
probabilités et indicateurs.

### 4.4 Contrôle

Ils vérifient la cohérence des résultats et détectent les anomalies.

### 4.5 Archivage

Ils déplacent les données historiques vers les espaces de conservation
prévus.

## 5. Dépendances

Chaque traitement déclare explicitement :

-   ses prérequis ;
-   ses données d'entrée ;
-   ses données de sortie ;
-   les traitements suivants pouvant être exécutés.

## 6. Politique de reprise

En cas d'échec :

1.  journalisation de l'erreur ;
2.  conservation du contexte ;
3.  nouvelle tentative selon la politique définie ;
4.  alerte si le seuil maximal est atteint.

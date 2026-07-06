# L008_BASE_SQL_v2.0.md --- Partie 1/3

# 1. Objet

Ce document présente l'architecture SQL de TurfIA. Il décrit les
principes de structuration de la base relationnelle, les responsabilités
des principaux ensembles de données et les choix de conception
garantissant cohérence, performance et évolutivité.

# 2. Principes

La base de données est organisée selon les principes suivants :

-   normalisation des données ;
-   intégrité référentielle ;
-   historisation des traitements ;
-   séparation des référentiels et des données d'exploitation ;
-   optimisation des lectures analytiques.

# 3. Vue logique

``` mermaid
flowchart TD
REF[Référentiels]
COURSES[Courses]
ANALYSES[Analyses]
RESULTATS[Résultats]
ADMIN[Administration]

REF --> COURSES
COURSES --> ANALYSES
ANALYSES --> RESULTATS
RESULTATS --> ADMIN
```

# 4. Domaines SQL

  Domaine          Finalité
  ---------------- -----------------------------------
  Référentiels     Entités permanentes
  Métier           Courses, analyses, paris
  Historique       Résultats et ROI
  Administration   Paramètres, journaux, supervision

*Fin de la partie 1/3.*

# L008_BASE_SQL_v2.0.md --- Partie 1/3

# 1. Objet

Ce document présente l'architecture SQL de TurfIA. Il décrit les
principes de structuration de la base relationnelle, les responsabilités
des principaux ensembles de données et les choix de conception
garantissant cohérence, performance et évolutivité.

## 1.1 Positionnement vis-à-vis des autres documents

Ce document décrit l'architecture SQL au niveau des choix structurants
(normalisation, domaines, intégrité). Le schéma physique complet
(tables, colonnes, types) est spécifié en L011 ; les vues en L012 ; les
migrations en L013 ; le dictionnaire de données exhaustif en L030.x.

## 1.2 Choix du système de gestion de base de données

PostgreSQL est retenu comme SGBD unique (cf. ADR-005 de L001) pour ses
garanties transactionnelles ACID, son support natif des contraintes
d'intégrité référentielle et des index avancés, et sa maturité
opérationnelle. Aucune alternative NoSQL n'est nécessaire tant que les
données restent structurées et les volumes compatibles avec les seuils
définis en L024/L036.

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

## 4.1 Schémas SQL et isolation logique

Chaque domaine est isolé logiquement (schéma PostgreSQL ou convention
de préfixe de table, cf. L011) afin de faciliter la lecture des droits
d'accès et la mise en place de permissions différenciées (cf. L021) :
les comptes applicatifs de lecture analytique n'ont, par exemple, pas
de droit d'écriture sur les référentiels.

*Fin de la partie 1/3.*

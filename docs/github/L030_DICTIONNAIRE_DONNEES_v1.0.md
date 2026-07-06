# L030 --- Dictionnaire de données

## 1. Objectif

Le présent document constitue la spécification détaillée du dictionnaire
de données de TurfIA.

Il décrit exhaustivement les tables, colonnes, types, contraintes et
relations. Il sert de référence unique pour les scripts SQL, l'ORM
Python et l'API REST.

## 2. Conventions

-   Clé primaire : `id`
-   Clés étrangères : `id_<table>`
-   Dates : `DATE`
-   Horodatages : `TIMESTAMP`
-   Booléens : `BOOLEAN`
-   Scores : `DECIMAL(5,2)` compris entre 0 et 100.

## 3. Table `hippodrome`

  Colonne    Type           Contraintes   Description
  ---------- -------------- ------------- ------------------
  id         BIGINT         PK            Identifiant
  nom        VARCHAR(100)   UNIQUE        Nom officiel
  ville      VARCHAR(80)                  Ville
  pays       VARCHAR(50)                  Pays
  corde_id   BIGINT         FK            Sens de la corde

## 4. Table `reunion`

  Colonne         Type       Contraintes   Description
  --------------- ---------- ------------- -----------------
  id              BIGINT     PK            Identifiant
  date            DATE       INDEX         Date de réunion
  hippodrome_id   BIGINT     FK            Hippodrome
  numero          SMALLINT                 Numéro

## 5. Table `course`

  Colonne         Type            Contraintes   Description
  --------------- --------------- ------------- -------------
  id              BIGINT          PK            Identifiant
  reunion_id      BIGINT          FK            Réunion
  numero          SMALLINT                      Numéro
  nom             VARCHAR(150)                  Libellé
  heure_depart    TIMESTAMP       INDEX         Départ
  discipline_id   BIGINT          FK            Discipline
  distance_id     BIGINT          FK            Distance
  allocation      DECIMAL(12,2)                 Allocation

## 6. Suite du document

Le dictionnaire détaillera ensuite de manière identique toutes les
tables du modèle :

-   cheval
-   jockey
-   entraineur
-   partant
-   cote
-   resultat
-   analyse
-   analyse_partant
-   selection
-   pari
-   controle_roi
-   statistique\_\*
-   configuration
-   migration
-   journal
-   tache
-   version

Chaque table sera décrite avec : - définition fonctionnelle ; - colonnes
; - contraintes ; - index ; - relations ; - règles métier.

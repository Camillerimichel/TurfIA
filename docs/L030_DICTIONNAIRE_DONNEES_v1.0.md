# L030 --- Dictionnaire de données

## 0. Métadonnées du document

| Champ | Valeur |
| --- | --- |
| Identifiant | L030 (index) |
| Niveau documentaire | Spécification technique (cf. L001 §3) |
| Version | 1.0 |
| Sous-documents | L030.1 (référentiels), L030.2 (tables métier), L030.3 (analyse), L030.4 (statistiques), L030.5 (techniques), L030.6 (relations/index) |
| Document parent | L011 (Schéma SQL), L004 (Modèle de données) |

Ce document sert de table des matières et de conventions communes ; le
détail exhaustif de chaque table est réparti dans les sous-documents
L030.1 à L030.6 afin de garder chaque livrable à une taille lisible.

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

## 7. Table de correspondance des sous-documents

| Sous-document | Contenu                                            |
| --------------- | ----------------------------------------------------- |
| L030.1           | Référentiels (hippodrome, discipline, surface...)      |
| L030.2           | Tables métier (réunion, course, cheval, partant...)    |
| L030.3           | Tables d'analyse (analyse, sélection, pari...)          |
| L030.4           | Tables statistiques                                     |
| L030.5           | Tables techniques (configuration, migration, journal...) |
| L030.6           | Relations et index transverses                          |

## 8. Gouvernance du dictionnaire

Toute création ou modification de table est reflétée simultanément
dans le sous-document L030.x concerné, dans le schéma physique (L011)
et dans les migrations (L013). Une divergence entre le dictionnaire et
le schéma réel est un défaut de gouvernance documentaire (cf. L001 §9).

---

## Historique

| Version | Description |
| --- | --- |
| 1.0 | Version initiale |
| 1.1 | Enrichissement industriel : métadonnées du document, table de correspondance des sous-documents, règle de gouvernance du dictionnaire |

*Fin du document L030 (index).*

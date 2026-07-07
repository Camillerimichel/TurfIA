# L011 — Schéma SQL

## 0. Métadonnées du document

| Champ | Valeur |
| --- | --- |
| Identifiant | L011 |
| Niveau documentaire | Spécification technique (cf. L001 §3) |
| Version | 1.0 |
| SGBD cible | PostgreSQL (cf. L008 §1.2) |
| Encodage | UTF-8, collation `fr_FR.UTF-8` pour le tri des libellés |
| Documents liés | L004 (modèle logique), L008 (architecture SQL), L012 (vues), L013 (migrations), L030.x (dictionnaire de données) |

## 1. Objectif

### 1.1 Finalité

Le schéma SQL constitue le référentiel de données de TurfIA.

Il décrit l'ensemble des objets relationnels nécessaires au fonctionnement de l'application :

- référentiels ;
- données hippiques ;
- analyses ;
- historiques ;
- statistiques ;
- paramètres ;
- journalisation.

Le schéma constitue la seule source officielle de stockage des données métier.

---

### 1.2 Objectifs

Le modèle doit garantir :

- l'intégrité des données ;
- la cohérence des analyses ;
- les performances de lecture ;
- la simplicité des évolutions ;
- la reproductibilité des calculs ;
- la traçabilité des traitements.

---

### 1.3 Principes

Le schéma est conçu pour :

- éviter les redondances ;
- limiter les traitements SQL complexes ;
- conserver l'historique complet des analyses ;
- permettre l'ajout de nouveaux critères sans remettre en cause le modèle.

---

## 2. Principes de conception

### 2.1 Architecture relationnelle

Le modèle repose sur une architecture relationnelle normalisée.

Les principales caractéristiques sont :

- clés primaires numériques ;
- clés étrangères systématiques ;
- intégrité référentielle ;
- transactions ACID ;
- index dédiés aux traitements fréquents.

---

### 2.2 Séparation des responsabilités

Les données sont réparties selon leur rôle.

| Catégorie    | Contenu                          |
| ------------ | -------------------------------- |
| Référentiels | données stables                  |
| Métier       | courses, chevaux, entraîneurs... |
| Analyses     | calculs TurfIA                   |
| Statistiques | ROI, historiques                 |
| Technique    | paramètres, logs, migrations     |

---

### 2.3 Historisation

Aucune donnée importante n'est écrasée.

Les modifications donnent lieu :

- à une nouvelle version ;
- ou à un nouvel enregistrement.

Cette approche garantit la reproductibilité des analyses plusieurs années après leur exécution.

---

### 2.4 Identifiants

Toutes les tables utilisent un identifiant technique.

```
id BIGINT
```

Les identifiants fonctionnels (numéro de course, code hippodrome, etc.) ne sont jamais utilisés comme clé primaire.

---

### 2.5 Dates

Toutes les dates sont stockées au format SQL standard.

Les règles suivantes s'appliquent :

- date → DATE
- date et heure → TIMESTAMP
- durée → INTERVAL ou entier selon le besoin.

Toutes les dates sont enregistrées dans le même fuseau horaire.

---

### 2.6 Colonnes d'audit

Toute table métier mutable comporte, en complément des colonnes
fonctionnelles, deux colonnes d'audit techniques :

```
cree_le      TIMESTAMP NOT NULL DEFAULT now()
modifie_le   TIMESTAMP
```

Ces colonnes ne remplacent pas l'historisation fonctionnelle (§15) :
elles permettent uniquement de diagnostiquer techniquement une
anomalie d'exploitation.

---

### 2.7 Contraintes NOT NULL

Toute colonne dont l'absence rendrait l'enregistrement inexploitable
par les traitements (ex. `course.reunion_id`, `partant.cheval_id`) est
déclarée `NOT NULL`. L'absence de valeur constitue une anomalie de
collecte et doit être détectée avant l'insertion (cf. L009, L023),
non tolérée silencieusement par une valeur nulle en base.

---

### 2.8 Actions référentielles (ON DELETE / ON UPDATE)

| Cas                                             | Action                     |
| ------------------------------------------------ | -------------------------- |
| Référentiel utilisé par une donnée métier          | `ON DELETE RESTRICT`       |
| Table de détail d'une entité métier (ex. `analyse_partant` → `analyse`) | `ON DELETE CASCADE` limité aux tables techniques/de détail non historisées |
| Donnée historisée (`analyse`, `resultat`, `controle_roi`) | `ON DELETE RESTRICT` (suppression interdite, cf. §15) |

Aucune suppression en cascade n'affecte une donnée historisée, conformément
au principe d'historisation immuable (cf. ADR-001 de L008).

---

## 3. Conventions de nommage

### 3.1 Langue

L'ensemble du schéma utilise des noms français.

Exemples :

- cheval
- course
- reunion
- hippodrome
- analyse

---

### 3.2 Nom des tables

Les tables sont nommées :

- en minuscules ;
- sans accent ;
- avec le caractère "_".

Exemples :

```
cheval
course
analyse_course
historique_roi
```

---

### 3.3 Colonnes

Les colonnes suivent les mêmes règles.

Exemples :

```
date_course
numero_course
distance
allocation
score_confiance
```

---

### 3.4 Clés primaires

Toutes les clés primaires utilisent le même nom.

```
id
```

---

### 3.5 Clés étrangères

Les clés étrangères utilisent :

```
id_course
id_cheval
id_jockey
id_entraineur
```

---

### 3.6 Tables de liaison

Les tables d'association utilisent les deux noms reliés.

Exemples :

```
course_cheval
cheval_entraineur
course_analyse
```

---

### 3.7 Contraintes

Les contraintes utilisent une nomenclature homogène.

```
pk_
fk_
idx_
uk_
ck_
```

Exemples :

```
pk_course
fk_course_reunion
idx_course_date
uk_cheval_nom
```

---

## 4. Types de données

### 4.1 Identifiants

```
BIGINT
```

Utilisé pour toutes les clés.

---

### 4.2 Chaînes

```
VARCHAR
```

Longueur adaptée à la donnée.

Exemples :

```
VARCHAR(30)
VARCHAR(80)
VARCHAR(255)
```

---

### 4.3 Texte long

```
TEXT
```

Utilisé pour :

- commentaires ;
- observations ;
- rapports.

---

### 4.4 Valeurs numériques

Entiers :

```
SMALLINT
INTEGER
BIGINT
```

Décimaux :

```
DECIMAL(p,s)
```

Utilisés notamment pour :

- cotes ;
- gains ;
- ROI ;
- allocations.

---

### 4.5 Booléens

```
BOOLEAN
```

Exemples :

```
non_partant
jouer
favori
```

---

### 4.6 Dates

```
DATE
TIMESTAMP
```

---

### 4.7 Pourcentages

Tous les pourcentages utilisent :

```
DECIMAL(5,2)
```

Exemples :

```
87.45
12.30
100.00
```

---

### 4.8 Scores

Les scores TurfIA utilisent :

```
DECIMAL(5,2)
```

Valeurs comprises entre :

```
0.00

et

100.00
```

---

## 5. Organisation du schéma

### 5.1 Vue d'ensemble

Le schéma est organisé selon les familles suivantes :

```
Référentiels

Métier

Analyses

Historiques

Statistiques

Technique
```

---

### 5.2 Référentiels

Contiennent les données relativement stables :

- hippodromes ;
- disciplines ;
- surfaces ;
- cordes ;
- types de courses ;
- distances ;
- allocations.

---

### 5.3 Métier

Contiennent les données quotidiennes :

- réunions ;
- courses ;
- partants ;
- chevaux ;
- jockeys ;
- entraîneurs ;
- cotes.

---

### 5.4 Analyses

Produites par TurfIA :

- score ;
- ROI théorique ;
- niveau de risque ;
- classement ;
- bases ;
- outsiders ;
- tocards.

---

### 5.5 Historiques

Conservent l'intégralité des analyses.

Aucune suppression n'est réalisée.

---

### 5.6 Statistiques

Calculées automatiquement :

- ROI global ;
- ROI par hippodrome ;
- ROI par discipline ;
- ROI par score ;
- taux de réussite ;
- gains cumulés.

---

### 5.7 Technique

Regroupe :

- paramètres ;
- migrations ;
- journaux ;
- versions ;
- tâches planifiées ;
- configuration.

---

### 5.8 Évolutivité

Cette organisation permet d'ajouter de nouvelles tables sans remettre en cause les relations existantes.

Le schéma est conçu pour accompagner les futures évolutions de TurfIA tout en préservant la compatibilité avec les données historiques.

## 6. Tables de référence

### 6.1 Objectif

Les tables de référence regroupent les données faiblement évolutives utilisées par l'ensemble des traitements de TurfIA.

Elles permettent :

- d'éviter les doublons ;
- de garantir la cohérence des données ;
- de simplifier les évolutions du modèle.

---

### 6.2 Vue d'ensemble

| Table            | Description                   |
| ---------------- | ----------------------------- |
| hippodrome       | Liste des hippodromes         |
| discipline       | Plat, Trot, Obstacle...       |
| type_course      | Handicap, Groupe, Réclamer... |
| corde            | Gauche, Droite                |
| surface          | Gazon, PSF, Cendrée...        |
| distance         | Distances officielles         |
| meteo            | Conditions météorologiques    |
| etat_piste       | Bon, Souple, Lourd...         |
| allocation       | Référentiel des allocations   |
| categorie_course | Groupe I, II, III, Listed...  |

---

### 6.3 Table hippodrome

| Champ       | Type         | Description      |
| ----------- | ------------ | ---------------- |
| id          | BIGINT       | Clé primaire     |
| nom         | VARCHAR(100) | Nom officiel     |
| pays        | VARCHAR(50)  | Pays             |
| ville       | VARCHAR(80)  | Ville            |
| corde_id    | BIGINT       | Sens de la corde |
| altitude    | INTEGER      | Altitude         |
| commentaire | TEXT         | Observations     |

---

### 6.4 Table discipline

| Champ       | Type        |
| ----------- | ----------- |
| id          | BIGINT      |
| libelle     | VARCHAR(40) |
| description | TEXT        |

Exemples :

- Plat
- Trot Attelé
- Trot Monté
- Haies
- Steeple
- Cross

---

### 6.5 Table type_course

| Champ       | Type        |
| ----------- | ----------- |
| id          | BIGINT      |
| libelle     | VARCHAR(80) |
| description | TEXT        |

---

### 6.6 Table surface

| Champ   | Type        |
| ------- | ----------- |
| id      | BIGINT      |
| libelle | VARCHAR(40) |

---

### 6.7 Table etat_piste

| Champ   | Type         |
| ------- | ------------ |
| id      | BIGINT       |
| libelle | VARCHAR(50)  |
| indice  | DECIMAL(4,2) |

---

### 6.8 Table distance

| Champ    | Type        |
| -------- | ----------- |
| id       | BIGINT      |
| distance | INTEGER     |
| unite    | VARCHAR(10) |

---

## 7. Tables métier

### 7.1 Objectif

Les tables métier contiennent l'ensemble des informations quotidiennes exploitées par TurfIA.

Elles représentent le cœur du modèle de données.

---

### 7.2 Vue d'ensemble

```text
Réunion
    │
    ├──── Courses
                │
                ├──── Partants
                │         │
                │         ├── Cheval
                │         ├── Jockey
                │         ├── Entraîneur
                │         └── Cotes
                │
                └──── Résultats
```

---

### 7.3 Table reunion

| Champ         | Type      |
| ------------- | --------- |
| id            | BIGINT    |
| date          | DATE      |
| hippodrome_id | BIGINT    |
| numero        | SMALLINT  |
| debut         | TIMESTAMP |

---

### 7.4 Table course

| Champ          | Type          |
| -------------- | ------------- |
| id             | BIGINT        |
| reunion_id     | BIGINT        |
| numero         | SMALLINT      |
| nom            | VARCHAR(150)  |
| heure_depart   | TIMESTAMP     |
| discipline_id  | BIGINT        |
| type_course_id | BIGINT        |
| distance_id    | BIGINT        |
| surface_id     | BIGINT        |
| etat_piste_id  | BIGINT        |
| allocation     | DECIMAL(12,2) |
| nb_partants    | SMALLINT      |

---

### 7.5 Table cheval

| Champ          | Type          |
| -------------- | ------------- |
| id             | BIGINT        |
| nom            | VARCHAR(120)  |
| sexe           | CHAR(1)       |
| date_naissance | DATE          |
| pere           | VARCHAR(120)  |
| mere           | VARCHAR(120)  |
| gains          | DECIMAL(14,2) |
| musique        | VARCHAR(100)  |

---

### 7.6 Table jockey

| Champ   | Type         |
| ------- | ------------ |
| id      | BIGINT       |
| nom     | VARCHAR(120) |
| prenom  | VARCHAR(80)  |
| licence | VARCHAR(40)  |
| actif   | BOOLEAN      |

---

### 7.7 Table entraineur

| Champ  | Type         |
| ------ | ------------ |
| id     | BIGINT       |
| nom    | VARCHAR(120) |
| prenom | VARCHAR(80)  |
| actif  | BOOLEAN      |

---

### 7.8 Table partant

Cette table relie une course à un cheval.

| Champ         | Type         |
| ------------- | ------------ |
| id            | BIGINT       |
| course_id     | BIGINT       |
| cheval_id     | BIGINT       |
| jockey_id     | BIGINT       |
| entraineur_id | BIGINT       |
| numero        | SMALLINT     |
| corde         | SMALLINT     |
| poids         | DECIMAL(5,1) |
| valeur        | DECIMAL(5,2) |
| age           | SMALLINT     |
| ferrure       | VARCHAR(20)  |
| musique       | VARCHAR(80)  |

---

### 7.9 Table cote

| Champ      | Type         |
| ---------- | ------------ |
| id         | BIGINT       |
| partant_id | BIGINT       |
| operateur  | VARCHAR(30)  |
| cote       | DECIMAL(6,2) |
| date_maj   | TIMESTAMP    |

Une course peut posséder plusieurs centaines d'évolutions de cotes.

---

### 7.10 Table resultat

| Champ       | Type        |
| ----------- | ----------- |
| id          | BIGINT      |
| course_id   | BIGINT      |
| partant_id  | BIGINT      |
| classement  | SMALLINT    |
| temps       | VARCHAR(20) |
| ecart       | VARCHAR(30) |
| non_partant | BOOLEAN     |

---

## 8. Tables d'analyse

### 8.1 Objectif

Ces tables stockent l'ensemble des calculs réalisés par TurfIA.

Elles permettent de reproduire intégralement une analyse plusieurs années après son exécution.

---

### 8.2 Vue d'ensemble

```text
Course
      │
      ├──── Pré-analyse
      │
      ├──── Analyse finale
      │
      ├──── Sélection
      │
      ├──── Paris proposés
      │
      └──── Contrôle ROI
```

---

### 8.3 Table analyse

> **Nom physique** : la table est créée en base sous le nom `analyses` (et non
> `analyse`). Constaté à l'implémentation : PostgreSQL réserve `ANALYSE` comme alias
> de la commande `ANALYZE`, ce qui provoque une erreur de syntaxe dès que
> l'identifiant `analyse` (non qualifié par des guillemets) apparaît hors d'une
> position `CREATE TABLE` (ex. `REFERENCES analyse(id)`, listes d'identifiants dans
> `GRANT`). Le nom conceptuel « analyse » (une exécution du moteur TurfIA) est
> inchangé ; seul l'identifiant SQL physique diffère. Les colonnes `analyse_id` ne
> sont pas concernées.

| Champ           | Type         |
| --------------- | ------------ |
| id              | BIGINT       |
| course_id       | BIGINT       |
| version         | SMALLINT     |
| date_calcul     | TIMESTAMP    |
| score_confiance | DECIMAL(5,2) |
| risque          | DECIMAL(5,2) |
| roi_theorique   | DECIMAL(6,2) |
| decision        | VARCHAR(20)  |

Une course peut posséder plusieurs analyses successives.

---

### 8.4 Table analyse_partant

| Champ      | Type         |
| ---------- | ------------ |
| id         | BIGINT       |
| analyse_id | BIGINT       |
| partant_id | BIGINT       |
| score      | DECIMAL(6,2) |
| classement | SMALLINT     |
| consensus  | DECIMAL(5,2) |
| value_bet  | BOOLEAN      |

---

### 8.5 Table selection

| Champ          | Type        |
| -------------- | ----------- |
| id             | BIGINT      |
| analyse_id     | BIGINT      |
| type_selection | VARCHAR(30) |
| partant_id     | BIGINT      |

Types possibles :

- Base
- Chance régulière
- Outsider
- Tocard
- Écarté

---

### 8.6 Table pari

| Champ            | Type         |
| ---------------- | ------------ |
| id               | BIGINT       |
| analyse_id       | BIGINT       |
| type_pari        | VARCHAR(40)  |
| mise             | DECIMAL(8,2) |
| budget_reference | DECIMAL(8,2) |
| commentaire      | TEXT         |

---

### 8.7 Table controle_roi

| Champ       | Type          |
| ----------- | ------------- |
| id          | BIGINT        |
| analyse_id  | BIGINT        |
| resultat    | DECIMAL(10,2) |
| gains       | DECIMAL(10,2) |
| perte       | DECIMAL(10,2) |
| roi         | DECIMAL(8,2)  |
| commentaire | TEXT          |

Ces tables constituent le cœur de TurfIA et permettent d'assurer une traçabilité complète des décisions, des paris recommandés et des performances obtenues.

## 9. Tables statistiques

### 9.1 Objectif

Les tables statistiques centralisent les indicateurs calculés par TurfIA afin de mesurer les performances du modèle et de suivre son évolution.

Ces tables sont exclusivement alimentées par les traitements automatiques du projet.

---

### 9.2 Principes

Les statistiques sont :

- historisées ;
- recalculables ;
- indépendantes des analyses individuelles ;
- exploitables pour l'amélioration continue.

Aucune statistique n'est modifiée manuellement.

---

### 9.3 Vue d'ensemble

```text
Analyses
      │
      ├──── Statistiques journalières
      ├──── Statistiques hebdomadaires
      ├──── Statistiques mensuelles
      ├──── Statistiques annuelles
      └──── Statistiques globales
```

---

### 9.4 Table statistique_globale

| Champ               | Type          |
| ------------------- | ------------- |
| id                  | BIGINT        |
| date_calcul         | TIMESTAMP     |
| nb_courses          | INTEGER       |
| nb_courses_jouees   | INTEGER       |
| nb_courses_ignorees | INTEGER       |
| gains               | DECIMAL(12,2) |
| pertes              | DECIMAL(12,2) |
| profit              | DECIMAL(12,2) |
| roi                 | DECIMAL(8,2)  |

---

### 9.5 Table statistique_score

| Champ         | Type         |
| ------------- | ------------ |
| id            | BIGINT       |
| score_min     | DECIMAL(5,2) |
| score_max     | DECIMAL(5,2) |
| nb_courses    | INTEGER      |
| roi           | DECIMAL(8,2) |
| taux_reussite | DECIMAL(5,2) |

---

### 9.6 Table statistique_hippodrome

| Champ         | Type          |
| ------------- | ------------- |
| id            | BIGINT        |
| hippodrome_id | BIGINT        |
| nb_courses    | INTEGER       |
| gains         | DECIMAL(12,2) |
| pertes        | DECIMAL(12,2) |
| roi           | DECIMAL(8,2)  |

---

### 9.7 Table statistique_discipline

| Champ         | Type         |
| ------------- | ------------ |
| id            | BIGINT       |
| discipline_id | BIGINT       |
| nb_courses    | INTEGER      |
| roi           | DECIMAL(8,2) |

---

### 9.8 Table statistique_pari

| Champ     | Type          |
| --------- | ------------- |
| id        | BIGINT        |
| type_pari | VARCHAR(40)   |
| nb_paris  | INTEGER       |
| gains     | DECIMAL(12,2) |
| pertes    | DECIMAL(12,2) |
| roi       | DECIMAL(8,2)  |

---

### 9.9 Table statistique_modele

Cette table mesure l'évolution du modèle TurfIA.

| Champ          | Type         |
| -------------- | ------------ |
| id             | BIGINT       |
| version_modele | VARCHAR(20)  |
| date_debut     | DATE         |
| date_fin       | DATE         |
| nb_courses     | INTEGER      |
| roi            | DECIMAL(8,2) |
| commentaire    | TEXT         |

Chaque évolution du modèle pourra ainsi être comparée objectivement.

---

## 10. Tables techniques

### 10.1 Objectif

Les tables techniques assurent le fonctionnement interne de TurfIA.

Elles ne contiennent aucune donnée métier.

---

### 10.2 Vue d'ensemble

| Table         |
| ------------- |
| configuration |
| migration     |
| journal       |
| tache         |
| version       |
| parametre     |
| utilisateur   |
| role          |

---

### 10.3 Table configuration

| Champ       | Type         |
| ----------- | ------------ |
| id          | BIGINT       |
| cle         | VARCHAR(120) |
| valeur      | TEXT         |
| description | TEXT         |

---

### 10.4 Table parametre

Les paramètres métiers sont stockés dans une table dédiée.

Exemples :

- pondération consensus
- pondération cotes
- pondération entraîneur
- pondération jockey
- pondération historique
- pondération hippodrome

Cette approche permet de faire évoluer le modèle sans modifier le code.

---

### 10.5 Table migration

| Champ          | Type        |
| -------------- | ----------- |
| id             | BIGINT      |
| version        | VARCHAR(40) |
| date_execution | TIMESTAMP   |
| duree          | INTEGER     |
| resultat       | VARCHAR(20) |

---

### 10.6 Table journal

Historique des événements techniques.

| Champ          | Type        |
| -------------- | ----------- |
| id             | BIGINT      |
| date_evenement | TIMESTAMP   |
| niveau         | VARCHAR(20) |
| composant      | VARCHAR(60) |
| message        | TEXT        |

---

### 10.7 Table tache

Historique des tâches automatiques.

| Champ       | Type         |
| ----------- | ------------ |
| id          | BIGINT       |
| nom         | VARCHAR(100) |
| debut       | TIMESTAMP    |
| fin         | TIMESTAMP    |
| resultat    | VARCHAR(20)  |
| commentaire | TEXT         |

---

### 10.8 Table version

| Champ            | Type        |
| ---------------- | ----------- |
| id               | BIGINT      |
| version          | VARCHAR(20) |
| date_publication | TIMESTAMP   |
| commit_git       | VARCHAR(80) |
| commentaire      | TEXT        |

---

## 11. Relations

### 11.1 Principes

Toutes les relations utilisent des clés étrangères.

Les suppressions en cascade sont limitées aux tables techniques.

Les données métier et historiques ne sont jamais supprimées automatiquement.

---

### 11.2 Schéma relationnel simplifié

```text
Hippodrome
      │
      └──── Réunion
                │
                └──── Course
                          │
                          ├──── Partant
                          │         │
                          │         ├── Cheval
                          │         ├── Jockey
                          │         └── Entraîneur
                          │
                          ├──── Résultat
                          │
                          └──── Analyse
                                    │
                                    ├── Analyse_partant
                                    ├── Sélection
                                    ├── Pari
                                    └── Contrôle_ROI
```

---

### 11.3 Cardinalités principales

| Relation                  | Cardinalité |
| ------------------------- | ----------- |
| Hippodrome → Réunion      | 1 → N       |
| Réunion → Course          | 1 → N       |
| Course → Partant          | 1 → N       |
| Cheval → Partant          | 1 → N       |
| Jockey → Partant          | 1 → N       |
| Entraîneur → Partant      | 1 → N       |
| Course → Analyse          | 1 → N       |
| Analyse → Analyse_partant | 1 → N       |
| Analyse → Sélection       | 1 → N       |
| Analyse → Pari            | 1 → N       |

---

## 12. Contraintes d'intégrité

### 12.1 Objectif

Les contraintes garantissent la cohérence des données enregistrées.

Elles permettent d'éviter les incohérences avant même l'exécution des règles métier.

---

### 12.2 Clés primaires

Chaque table possède une clé primaire unique.

Toutes les clés utilisent le champ :

```text
id
```

---

### 12.3 Clés étrangères

Toutes les relations sont protégées par des contraintes de type `FOREIGN KEY`.

Les données orphelines sont interdites.

---

### 12.4 Contraintes d'unicité

Les contraintes `UNIQUE` sont utilisées notamment pour :

- un hippodrome ;
- une discipline ;
- une course dans une réunion ;
- un cheval ;
- une version du modèle.

---

### 12.5 Contraintes métier

Les contraintes `CHECK` garantissent notamment :

- Score TurfIA compris entre 0 et 100 ;
- ROI calculable ;
- classement strictement positif ;
- numéro de partant valide ;
- budget supérieur ou égal à zéro ;
- mise supérieure ou égale à zéro.

---

### 12.6 Philosophie

Les contraintes SQL garantissent la cohérence structurelle.

Les décisions TurfIA, les calculs de score, les pondérations et les règles de sélection restent exclusivement implémentés dans la couche métier afin de préserver l'évolutivité du modèle.

## 13. Index

### 13.1 Objectif

Les index permettent d'optimiser les temps d'accès aux données sans modifier le modèle relationnel.

Ils sont créés uniquement lorsqu'ils apportent un gain mesurable sur les traitements les plus fréquents.

L'ajout d'un index doit toujours être justifié par une analyse des performances.

---

### 13.2 Principes

Les règles suivantes s'appliquent :

- un index répond à un besoin identifié ;
- éviter les index redondants ;
- privilégier les index composites lorsque plusieurs colonnes sont systématiquement utilisées ensemble ;
- limiter les index sur les tables fortement mises à jour ;
- contrôler régulièrement leur utilisation.

---

### 13.3 Index des référentiels

Les principales tables de référence possèdent un index sur leur libellé.

| Table       | Colonnes indexées |
| ----------- | ----------------- |
| hippodrome  | nom               |
| discipline  | libelle           |
| surface     | libelle           |
| type_course | libelle           |

---

### 13.4 Index des courses

Les recherches quotidiennes utilisent principalement :

| Table   | Colonnes      |
| ------- | ------------- |
| reunion | date          |
| reunion | hippodrome_id |
| course  | reunion_id    |
| course  | heure_depart  |
| course  | discipline_id |
| course  | distance_id   |

---

### 13.5 Index des partants

Les traitements TurfIA utilisent principalement :

| Table   | Colonnes      |
| ------- | ------------- |
| partant | course_id     |
| partant | cheval_id     |
| partant | jockey_id     |
| partant | entraineur_id |
| partant | numero        |

---

### 13.6 Index des analyses

Les analyses étant consultées très fréquemment, plusieurs index sont nécessaires.

| Table           | Colonnes        |
| --------------- | --------------- |
| analyse         | course_id       |
| analyse         | score_confiance |
| analyse         | date_calcul     |
| analyse_partant | analyse_id      |
| analyse_partant | partant_id      |
| selection       | analyse_id      |

---

### 13.7 Index statistiques

Les statistiques sont principalement consultées selon :

- la date ;
- le score ;
- l'hippodrome ;
- la discipline ;
- le type de pari.

Les index sont créés sur ces colonnes afin d'accélérer les tableaux de bord.

---

### 13.8 Index composites

Les index composites sont privilégiés lorsque plusieurs colonnes sont systématiquement utilisées ensemble.

Exemples :

| Table    | Colonnes              |
| -------- | --------------------- |
| course   | reunion_id, numero    |
| cote     | partant_id, date_maj  |
| resultat | course_id, classement |
| analyse  | course_id, version    |

---

### 13.9 Maintenance

Les index sont régulièrement contrôlés afin de :

- supprimer les index inutilisés ;
- reconstruire les index dégradés ;
- analyser leur impact sur les performances.

Cette maintenance est intégrée aux opérations d'exploitation.

---

## 14. Performances

### 14.1 Objectif

L'architecture SQL est conçue pour assurer des temps de réponse compatibles avec une utilisation quotidienne intensive.

Les performances doivent rester stables malgré l'augmentation progressive des volumes de données.

---

### 14.2 Principes

Les optimisations privilégient :

- la simplicité des requêtes ;
- la lisibilité du modèle ;
- l'utilisation des index ;
- la limitation des jointures inutiles.

La performance ne doit jamais compromettre la maintenabilité.

---

### 14.3 Optimisation des lectures

Les traitements les plus fréquents concernent :

- les analyses du Quinté du jour ;
- les historiques des chevaux ;
- les statistiques TurfIA ;
- les tableaux de bord.

Ces traitements doivent être optimisés en priorité.

---

### 14.4 Optimisation des écritures

Les écritures sont principalement réalisées :

- lors des importations ;
- lors des analyses quotidiennes ;
- lors des contrôles de résultats ;
- lors des calculs statistiques.

Les transactions doivent rester courtes afin de limiter les verrouillages.

---

### 14.5 Vues SQL

Les vues simplifient les requêtes de consultation.

Elles sont utilisées notamment pour :

- les tableaux de bord ;
- les statistiques ;
- les exports ;
- les rapports.

Les vues complexes pourront être matérialisées si les volumes le justifient.

---

### 14.6 Archivage

Les données historiques restent accessibles.

Cependant, les traitements quotidiens privilégient les données récentes afin de limiter les volumes parcourus.

Une politique d'archivage pourra être mise en place sans modifier le modèle relationnel.

---

### 14.7 Évolution des performances

La surveillance porte notamment sur :

- le temps moyen des requêtes ;
- les index les plus sollicités ;
- la croissance des tables ;
- la fragmentation des index ;
- les temps de sauvegarde.

Ces indicateurs alimentent la supervision de la plateforme.

---

## 15. Historisation

### 15.1 Objectif

L'historisation constitue un principe fondamental de TurfIA.

Elle permet de conserver l'ensemble des analyses réalisées afin de mesurer objectivement l'évolution du modèle.

---

### 15.2 Principes

Aucune analyse n'est supprimée.

Chaque exécution produit un nouvel enregistrement.

Cette approche garantit :

- la reproductibilité ;
- la traçabilité ;
- l'auditabilité.

---

### 15.3 Données historisées

Les éléments suivants sont conservés :

- analyses successives ;
- sélections ;
- paris proposés ;
- scores ;
- ROI théoriques ;
- résultats réels ;
- statistiques calculées.

---

### 15.4 Versionnement

Chaque analyse possède un numéro de version.

Exemple :

- Version 1 : pré-analyse
- Version 2 : analyse finale
- Version 3 : recalcul éventuel

Les versions précédentes restent consultables.

---

### 15.5 Exploitation

L'historique permet notamment :

- la comparaison de plusieurs versions du modèle ;
- l'analyse des erreurs ;
- la validation des nouvelles pondérations ;
- le calcul du ROI historique.

Cette base constitue un élément essentiel de l'amélioration continue.

---

## 16. Évolutivité

### 16.1 Objectif

Le schéma SQL est conçu pour accompagner les évolutions futures de TurfIA sans remise en cause des données existantes.

---

### 16.2 Principes

Toute évolution doit respecter les règles suivantes :

- compatibilité ascendante ;
- conservation des historiques ;
- migrations versionnées ;
- documentation systématique.

---

### 16.3 Extensions fonctionnelles

Le modèle permet notamment d'ajouter :

- de nouveaux types de paris ;
- de nouveaux critères de scoring ;
- de nouvelles disciplines hippiques ;
- de nouveaux indicateurs statistiques ;
- de nouvelles sources de données.

Ces évolutions ne nécessitent pas de refonte du schéma.

---

### 16.4 Montée en charge

Le modèle est conçu pour absorber :

- plusieurs millions de courses ;
- plusieurs dizaines de millions de cotes ;
- plusieurs centaines de millions de lignes d'historique.

L'architecture relationnelle reste compatible avec une évolution vers une infrastructure distribuée.

---

### 16.5 Sécurité et contrôle d'accès

L'accès à la base est cloisonné par des rôles applicatifs distincts,
conformément à L021 et L034 :

| Rôle applicatif        | Droits                                   | Usage                        |
| ------------------------ | ------------------------------------------ | ------------------------------ |
| `turfia_app`              | Lecture/écriture sur métier et analyses    | Services applicatifs           |
| `turfia_readonly`         | Lecture seule sur toutes les tables         | Tableaux de bord, exports      |
| `turfia_migration`        | DDL complet (création/altération de schéma) | Exécution des migrations (L013) uniquement |

Aucun compte applicatif ne dispose de droits `SUPERUSER`. L'accès direct
à la base en dehors de ces rôles est réservé aux opérations
d'administration exceptionnelles, journalisées (cf. L025).

---

### 16.6 Conclusion

Le schéma SQL constitue le socle de l'ensemble de TurfIA.

Son organisation, sa normalisation et son historisation garantissent :

- la cohérence des données ;
- la reproductibilité des analyses ;
- la mesure objective des performances ;
- la capacité d'évolution du projet.

Il constitue la référence unique pour le développement des scripts SQL, des migrations, des vues, de l'API et des traitements automatiques.

---

## Historique

| Version | Description |
| --- | --- |
| 1.0 | Version initiale |
| 1.1 | Enrichissement industriel : métadonnées du document, colonnes d'audit, contraintes NOT NULL, actions référentielles ON DELETE/ON UPDATE, sécurité et contrôle d'accès par rôles applicatifs |
| 1.2 | Correction post-implémentation : la table `analyse` est physiquement nommée `analyses` (collision avec le mot-clé PostgreSQL ANALYSE/ANALYZE), constaté lors de la vérification de la première implémentation (cf. §8.3) |

*Fin du document L011.*
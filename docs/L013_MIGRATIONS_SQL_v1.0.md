# L013 — Migrations SQL

## 0. Métadonnées du document

| Champ | Valeur |
| --- | --- |
| Identifiant | L013 |
| Niveau documentaire | Spécification technique (cf. L001 §3) |
| Version | 1.0 |
| Dépend de | L011 (Schéma SQL) |
| Consommé par | L010 (Déploiement), L025 (Exploitation) |

## 1. Objectif

### 1.1 Finalité

Les migrations SQL assurent l'évolution contrôlée du schéma de données de TurfIA.

Elles garantissent que chaque environnement (développement, préproduction et production) possède exactement la même structure de base de données.

Aucune modification manuelle du schéma n'est autorisée.

---

### 1.2 Principes

Chaque migration est :

- unique ;
- versionnée ;
- traçable ;
- reproductible ;
- documentée.

Une migration exécutée ne doit jamais être modifiée.

Toute évolution ultérieure fait l'objet d'une nouvelle migration.

---

## 2. Organisation

### 2.1 Arborescence

Les migrations sont stockées dans le répertoire :

```text
sql/
└── migrations/
```

---

### 2.2 Convention de nommage

Chaque migration suit la convention suivante :

```text
YYYYMMDD_HHMM_description.sql
```

Exemples :

```text
20260701_0900_creation_schema.sql

20260703_1430_creation_tables_reference.sql

20260705_1030_creation_tables_metier.sql

20260708_1815_creation_index.sql
```

Le classement chronologique garantit un ordre d'exécution unique.

---

### 2.3 Responsable et revue

Toute migration est proposée par un développeur et revue par
l'architecte logiciel avant intégration (cf. RACI de gouvernance
d'architecture, L003 §10.1), au même titre qu'une évolution de code
applicatif. Une migration n'est jamais appliquée directement en
production sans avoir été exécutée préalablement en environnement de
recette (cf. L010 §4.1).

---

## 3. Cycle de vie d'une migration

### 3.1 Création

Une migration est créée lorsqu'une évolution concerne :

- une table ;
- une vue ;
- un index ;
- une contrainte ;
- une procédure ;
- un déclencheur.

---

### 3.2 Validation

Avant toute intégration :

- la migration est exécutée sur une base vierge ;
- elle est exécutée sur une base existante ;
- les performances sont contrôlées ;
- les contraintes sont validées.

---

### 3.3 Déploiement

Les migrations sont exécutées automatiquement lors du déploiement.

Le système vérifie les versions déjà installées.

Une migration déjà exécutée n'est jamais rejouée.

---

## 4. Table de suivi

### 4.1 Objectif

Toutes les migrations exécutées sont historisées.

Cette table permet notamment :

- d'identifier la version du schéma ;
- de reprendre une installation interrompue ;
- d'effectuer des audits.

---

### 4.2 Structure

| Champ          | Type         |
| -------------- | ------------ |
| id             | BIGINT       |
| version        | VARCHAR(40)  |
| fichier        | VARCHAR(255) |
| date_execution | TIMESTAMP    |
| duree_ms       | INTEGER      |
| resultat       | VARCHAR(20)  |
| checksum       | VARCHAR(128) |

---

## 5. Types de migrations

### 5.1 Création

Exemples :

- création d'une table ;
- création d'un index ;
- création d'une vue.

---

### 5.2 Modification

Exemples :

- ajout d'une colonne ;
- modification d'un type ;
- ajout d'une contrainte.

---

### 5.3 Suppression

La suppression d'objets reste exceptionnelle.

Avant toute suppression :

- analyse d'impact ;
- sauvegarde ;
- documentation.

---

### 5.4 Migration de données

Certaines migrations déplacent ou recalculent des données.

Ces traitements doivent être :

- transactionnels ;
- rejouables ;
- documentés.

---

## 6. Transactions

Toutes les migrations exécutables de manière atomique sont encapsulées dans une transaction.

En cas d'échec :

- annulation complète ;
- aucune modification partielle ;
- journalisation de l'erreur.

---

## 7. Compatibilité

Une migration ne doit jamais rendre les données historiques incompatibles.

Les principes suivants s'appliquent :

- compatibilité ascendante ;
- conservation des historiques ;
- conservation des identifiants ;
- préservation des clés étrangères.

---

## 8. Vérifications

Chaque migration est suivie automatiquement de contrôles portant sur :

- la présence des nouveaux objets ;
- l'intégrité référentielle ;
- les index ;
- les vues ;
- les contraintes.

---

## 9. Rollback

Lorsque cela est possible, une procédure de retour arrière est prévue.

Elle permet notamment :

- la suppression des objets créés ;
- la restauration des structures précédentes ;
- la récupération des sauvegardes.

Les migrations destructrices doivent rester exceptionnelles.

### 9.1 Stratégie pour les migrations non instantanément réversibles

Certaines migrations (ex. changement de type d'une colonne volumineuse)
ne peuvent pas être annulées instantanément. Dans ce cas, la migration
est conçue en plusieurs étapes rétro-compatibles (ex. ajout d'une
nouvelle colonne, double écriture temporaire, bascule, puis suppression
de l'ancienne colonne dans une migration ultérieure distincte) plutôt
que par un changement en place risqué.

---

## 10. Évolutivité

La stratégie de migration retenue permet :

- plusieurs centaines de versions ;
- des installations progressives ;
- des mises à jour automatiques ;
- une parfaite traçabilité de l'évolution du schéma SQL.

Elle constitue le mécanisme officiel d'évolution de la base de données de TurfIA.

### 10.1 Risques et hypothèses

| Risque                                              | Mitigation |
| ------------------------------------------------------ | ------------ |
| Migration longue verrouillant une table en production    | Exécution en heure creuse, migration en plusieurs étapes (§9.1) |
| Divergence entre schéma réel et migrations enregistrées   | Contrôle de checksum systématique (§4.2), interdiction de modifier une migration déjà exécutée |
| Perte de la table de suivi des migrations                 | Table de suivi incluse dans le périmètre de sauvegarde (cf. L038) |

---

## Historique

| Version | Description |
| --- | --- |
| 1.0 | Version initiale |
| 1.1 | Enrichissement industriel : métadonnées du document, responsable et revue des migrations, stratégie pour les migrations non instantanément réversibles, risques et hypothèses |

*Fin du document L013.*
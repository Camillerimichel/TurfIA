# L014 — Arborescence du projet

## 1. Objectif

### 1.1 Finalité

L'arborescence du projet définit l'organisation physique de l'ensemble des fichiers composant TurfIA.

Elle poursuit plusieurs objectifs :

- faciliter la maintenance ;
- isoler les responsabilités ;
- simplifier les développements ;
- permettre un déploiement automatisé ;
- rendre le projet facilement compréhensible.

Cette organisation constitue la référence officielle pour l'ensemble du dépôt GitHub.

---

## 2. Principes

### 2.1 Organisation

Chaque répertoire possède une responsabilité unique.

Le code métier ne doit jamais être mélangé avec :

- la documentation ;
- les scripts SQL ;
- les fichiers HTML ;
- les fichiers de configuration ;
- les tests.

---

### 2.2 Modularité

Chaque module doit pouvoir évoluer indépendamment.

Une modification dans un composant ne doit pas entraîner de modification importante des autres composants.

---

## 3. Arborescence générale

```text
TurfIA/

├── api/
├── automations/
├── config/
├── data/
├── docs/
├── html/
├── logs/
├── scripts/
├── sql/
├── src/
├── tests/
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── README.md
└── requirements.txt
```

---

## 4. Répertoire docs

### 4.1 Objectif

Contient l'ensemble de la documentation officielle.

```text
docs/

L001_README_v1.0.md

L002_VISION_v1.0.md

...

L014_ARBORESCENCE_v1.0.md
```

Aucune documentation ne doit être stockée ailleurs.

---

## 5. Répertoire sql

### 5.1 Organisation

```text
sql/

schema/

views/

migrations/

seeds/

tests/
```

---

### 5.2 schema

Contient :

- création des tables ;
- contraintes ;
- index.

---

### 5.3 views

Contient :

- vues SQL ;
- vues matérialisées.

---

### 5.4 migrations

Historique complet des migrations.

---

### 5.5 seeds

Jeux de données de référence.

---

## 6. Répertoire src

### 6.1 Objectif

Contient exclusivement le code métier.

```text
src/

core/

database/

models/

repositories/

services/

algorithms/

statistics/

utils/
```

---

### 6.2 core

Fonctions communes.

---

### 6.3 database

Connexion SQL.

---

### 6.4 models

Objets métier.

---

### 6.5 repositories

Accès aux données.

---

### 6.6 services

Règles métier.

---

### 6.7 algorithms

Calculs TurfIA.

---

### 6.8 statistics

Calculs statistiques.

---

## 7. Répertoire api

```text
api/

routes/

schemas/

dependencies/

middlewares/

security/
```

Les routes HTTP ne contiennent aucune logique métier.

---

## 8. Répertoire automations

```text
automations/

daily/

weekly/

monthly/

maintenance/

monitoring/
```

Les tâches planifiées sont regroupées par fréquence.

---

## 9. Répertoire html

```text
html/

templates/

static/

css/

js/

images/
```

Les ressources statiques sont séparées des modèles HTML.

---

## 10. Répertoire config

Contient uniquement :

- fichiers YAML ;
- fichiers JSON ;
- modèles de configuration.

Aucun secret n'est stocké dans ce répertoire.

---

## 11. Répertoire data

Répertoire destiné :

- aux imports ;
- aux exports ;
- aux fichiers temporaires.

Son contenu n'est pas versionné.

---

## 12. Répertoire logs

Les journaux applicatifs sont regroupés dans un répertoire unique.

Ils sont exclus du dépôt Git.

---

## 13. Répertoire tests

```text
tests/

unit/

integration/

performance/

fixtures/
```

Chaque nouveau module possède ses propres tests.

---

## 14. Évolutivité

Cette organisation permet :

- l'ajout de nouveaux modules ;
- la séparation future en micro-services ;
- l'intégration de nouvelles interfaces ;
- l'ajout de nouvelles automatisations ;
- la montée en charge de TurfIA.

Elle constitue l'organisation officielle du dépôt GitHub.
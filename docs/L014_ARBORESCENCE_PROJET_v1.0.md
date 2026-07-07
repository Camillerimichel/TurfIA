# L014 — Arborescence du projet

## 0. Métadonnées du document

| Champ | Valeur |
| --- | --- |
| Identifiant | L014 |
| Niveau documentaire | Spécification technique (cf. L001 §3) |
| Version | 1.0 |
| Documents liés | L015 (architecture du code source), L019 (standards de développement), L027 (gestion des versions Git) |

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

### 2.3 Ce qui n'est jamais versionné dans Git

Les répertoires et fichiers suivants sont exclus du dépôt via
`.gitignore`, conformément à L021 (Sécurité) et L027 (Gestion des
versions Git) :

- `data/` (contenu non versionné, cf. §11) ;
- `logs/` (journaux applicatifs, cf. §12) ;
- tout fichier contenant des secrets réels (les seuls fichiers
  d'exemple, comme `.env.example`, sont versionnés) ;
- les environnements virtuels et dépendances installées localement.

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

collecte/
```

---

### 6.1.1 Écart constaté à l'implémentation (collecte)

`src/collecte/` a été ajouté lors de l'implémentation de la collecte de données
(architecture multi-sources en 4 niveaux : données officielles, marché, consensus
presse, base TurfIA propriétaire — cf. PROJECT_STATE.md pour le détail et le statut
par source). Ce sous-répertoire n'était pas anticipé dans la version initiale de ce
document ; il regroupe les adaptateurs par source (ex. `collecte/pmu/`) derrière une
interface commune (`collecte/base.py`), au même niveau que `algorithms/` ou
`repositories/`.

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

### 14.1 Propriétaire par répertoire

| Répertoire     | Propriétaire fonctionnel                  |
| ---------------- | -------------------------------------------- |
| `src/`             | Développeurs (code métier)                    |
| `sql/`             | Architecte logiciel + développeurs (cf. L011-L013) |
| `api/`             | Développeurs API (cf. L007, L016)             |
| `automations/`      | Exploitation (cf. L017, L033)                 |
| `html/`             | Développeurs interface (cf. L018)             |
| `config/`           | Exploitation (cf. L026)                       |
| `tests/`            | Développeurs, revue croisée obligatoire (cf. L020) |
| `docs/`             | Architecte logiciel (gouvernance documentaire, cf. L028) |

### 14.2 Règle de non-régression de l'arborescence

Tout déplacement ou renommage d'un répertoire de premier niveau
constitue une décision d'architecture et suit le processus de
gouvernance défini en L003 §10 (analyse d'impact, mise à jour des ADR,
mise à jour de ce document) avant sa mise en œuvre.

---

## Historique

| Version | Description |
| --- | --- |
| 1.0 | Version initiale |
| 1.1 | Enrichissement industriel : métadonnées du document, éléments exclus du versionnement Git, propriétaire fonctionnel par répertoire, règle de non-régression de l'arborescence |
| 1.2 | Correction post-implémentation : ajout de `src/collecte/` (architecture multi-sources de collecte de données, non anticipé initialement), cf. §6.1.1 |

*Fin du document L014.*
# L015 — Architecture du code source

## 0. Métadonnées du document

| Champ | Valeur |
| --- | --- |
| Identifiant | L015 |
| Niveau documentaire | Spécification technique (cf. L001 §3) |
| Version | 1.0 |
| Langage | Python |
| Documents liés | L003 (architecture générale), L014 (arborescence), L019 (standards de développement), L020 (stratégie de tests) |

## 1. Objectif

### 1.1 Finalité

L'architecture logicielle de TurfIA repose sur une séparation stricte des responsabilités.

Chaque module possède un rôle clairement identifié afin de :

- faciliter les développements ;
- limiter les dépendances ;
- simplifier les tests ;
- améliorer la maintenance ;
- permettre l'évolution progressive du projet.

Aucun module ne doit cumuler plusieurs responsabilités.

---

## 2. Architecture générale

L'application est organisée selon une architecture en couches.

```text
               Interface HTML
                      │
                      ▼
                 API REST
                      │
                      ▼
               Services métier
                      │
          ┌───────────┼───────────┐
          │           │           │
     Algorithmes  Statistiques  Automatisations
          │           │           │
          └───────────┼───────────┘
                      ▼
                Repositories
                      │
                      ▼
                 Base SQL
```

Chaque couche ne communique qu'avec la couche immédiatement inférieure.

### 2.1 Correspondance avec les couches du SAD

Cette organisation en modules Python est la traduction directe de la
vue logique décrite en L003 : `services` correspond à la couche
« Services métier », `algorithms` et `statistics` au « Moteur TurfIA »,
`repositories`/`database` à la couche « Base SQL ». Toute divergence
entre ce document et L003 constitue un défaut de gouvernance
documentaire (cf. L028).

---

## 3. Module Core

### 3.1 Objectif

Le module `core` contient les composants communs utilisés par l'ensemble du projet.

Il regroupe notamment :

- constantes ;
- énumérations ;
- exceptions ;
- configuration ;
- journalisation ;
- outils génériques.

Aucun traitement métier spécifique n'y est implémenté.

---

## 4. Module Database

### 4.1 Objectif

Le module `database` assure toutes les communications avec la base SQL.

Il est responsable :

- de la connexion ;
- de l'ouverture des sessions ;
- des transactions ;
- de la fermeture des connexions.

Les autres modules n'accèdent jamais directement au moteur SQL.

### 4.2 Gestion du cycle de vie des connexions

Le module `database` expose les sessions sous forme de gestionnaire de
contexte (context manager), garantissant qu'une session est toujours
fermée (commit ou rollback explicite) même en cas d'exception. Aucun
appelant ne doit gérer manuellement l'ouverture/fermeture d'une
connexion bas niveau.

---

## 5. Module Models

### 5.1 Objectif

Le module `models` représente les objets métier manipulés par TurfIA.

Exemples :

- Cheval
- Course
- Réunion
- Partant
- Analyse
- Pari
- Résultat

Chaque modèle reflète une entité métier.

---

## 6. Module Repositories

### 6.1 Objectif

Les repositories centralisent les accès aux données.

Chaque repository est responsable d'une famille d'objets.

Exemples :

```text
ChevalRepository

CourseRepository

AnalyseRepository

StatistiqueRepository
```

Ils encapsulent toutes les requêtes SQL.

---

## 7. Module Services

### 7.1 Objectif

Les services implémentent les règles métier.

Ils orchestrent les traitements réalisés par TurfIA.

Exemples :

```text
AnalyseService

SelectionService

PariService

ROIService

StatistiqueService
```

Les services ne contiennent aucun code HTTP.

### 7.2 Contrat des services

Un service expose des méthodes prenant en entrée des objets du module
`models` (ou des types primitifs) et retournant des objets du module
`models` ou lève une exception métier typée (cf. L023). Un service
n'accepte jamais et ne retourne jamais directement d'objet de requête
ou de réponse HTTP : cette traduction est de la responsabilité exclusive
du module `api` (cf. L016).

---

## 8. Module Algorithms

### 8.1 Objectif

Ce module regroupe les algorithmes de calcul.

Il comprend notamment :

- calcul du score TurfIA ;
- estimation du ROI ;
- détection des value bets ;
- pondération des critères ;
- classement final.

Tous les calculs sont centralisés dans ce module.

---

### 8.2 Évolutivité

Chaque algorithme est indépendant.

Une nouvelle version peut être ajoutée sans supprimer les précédentes.

Cette approche permet de comparer objectivement les performances des différentes versions du modèle.

### 8.3 Pureté fonctionnelle

Conformément à L006 §4.2 et L009 §2.1, les fonctions de ce module sont
des fonctions pures : aucun accès base de données, aucun appel réseau,
aucune écriture de fichier. Toute donnée nécessaire est passée en
paramètre, tout résultat est retourné explicitement.

---

## 9. Module Statistics

### 9.1 Objectif

Le module Statistics calcule l'ensemble des indicateurs du projet.

Il produit notamment :

- ROI global ;
- ROI par hippodrome ;
- ROI par discipline ;
- ROI par score ;
- taux de réussite ;
- statistiques des paris.

Les traitements statistiques sont totalement indépendants des algorithmes de sélection.

---

## 10. Module Utils

### 10.1 Objectif

Le module `utils` regroupe les fonctions utilitaires réutilisables.

Exemples :

- manipulation des dates ;
- formatage ;
- conversions ;
- export CSV ;
- export JSON ;
- validation des paramètres.

Aucune règle métier ne doit être présente dans ce module.

---

## 11. Dépendances entre modules

Les dépendances suivent le schéma suivant :

```text
API
 │
 ▼
Services
 │
 ├────────► Algorithms
 │
 ├────────► Statistics
 │
 └────────► Repositories
                  │
                  ▼
               Database
```

Les dépendances circulaires sont interdites.

---

## 12. Injection de dépendances

Les services ne créent jamais directement leurs dépendances.

Les composants sont injectés au démarrage de l'application.

Cette approche facilite :

- les tests unitaires ;
- le remplacement d'un composant ;
- les évolutions futures.

---

## 13. Tests

Chaque module possède ses propres tests.

Exemple :

```text
tests/

core/

database/

repositories/

services/

algorithms/

statistics/
```

Les tests sont indépendants les uns des autres.

### 13.1 Correspondance module ↔ niveau de test

| Module         | Niveau de test principal        | Document |
| ---------------- | ---------------------------------- | ---------- |
| `algorithms`, `statistics` | Tests unitaires (fonctions pures)   | L020 |
| `services`        | Tests unitaires + tests d'intégration | L020 |
| `repositories`, `database` | Tests d'intégration (base réelle ou éphémère) | L020 |
| `api`             | Tests d'intégration/contrat (OpenAPI) | L007, L020 |

---

## 14. Convention de développement

Chaque nouveau composant respecte les règles suivantes :

- une responsabilité unique ;
- documentation obligatoire ;
- tests associés ;
- journalisation des erreurs ;
- gestion explicite des exceptions.

Le code doit rester lisible et facilement maintenable.

---

## 15. Évolutivité

Cette architecture permet d'intégrer facilement :

- de nouveaux algorithmes ;
- de nouvelles sources de données ;
- de nouveaux types de paris ;
- de nouveaux indicateurs statistiques ;
- une interface mobile ;
- une API publique.

Elle constitue la base de développement de TurfIA pour les prochaines évolutions du projet.

---

## Historique

| Version | Description |
| --- | --- |
| 1.0 | Version initiale |
| 1.1 | Enrichissement industriel : correspondance avec les couches du SAD, cycle de vie des connexions, contrat des services, pureté fonctionnelle des algorithmes, correspondance module/niveau de test |

*Fin du document L015.*
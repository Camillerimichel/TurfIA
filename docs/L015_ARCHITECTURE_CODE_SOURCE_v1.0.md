# L015 — Architecture du code source

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
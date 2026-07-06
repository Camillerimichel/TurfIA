# L026 — Gestion de la configuration

## 1. Objectif

### 1.1 Finalité

La gestion de la configuration regroupe l'ensemble des paramètres nécessaires au fonctionnement de TurfIA.

Elle poursuit plusieurs objectifs :

- séparer la configuration du code ;
- faciliter le déploiement ;
- sécuriser les informations sensibles ;
- simplifier les évolutions ;
- garantir la reproductibilité des environnements.

Aucun paramètre spécifique à un environnement ne doit être codé en dur.

---

## 2. Principes

### 2.1 Séparation

Les éléments suivants sont totalement indépendants :

- code source ;
- configuration ;
- données ;
- secrets.

Cette séparation permet de déployer une même version logicielle sur plusieurs environnements.

---

### 2.2 Centralisation

L'ensemble des paramètres est regroupé dans un mécanisme unique de configuration.

Les modules applicatifs ne lisent jamais directement les variables d'environnement.

---

## 3. Types de configuration

### 3.1 Configuration système

Elle comprend notamment :

- ports réseau ;
- chemins de fichiers ;
- paramètres Docker ;
- configuration Nginx ;
- planification des tâches.

---

### 3.2 Configuration applicative

Elle comprend notamment :

- paramètres TurfIA ;
- seuils de confiance ;
- budgets de référence ;
- pondérations ;
- paramètres statistiques.

Ces éléments peuvent évoluer sans modification du code.

---

### 3.3 Configuration métier

Les paramètres métier sont stockés en base de données.

Exemples :

- score minimum de jeu ;
- budget par niveau de confiance ;
- pondération des critères ;
- paramètres des algorithmes.

---

## 4. Variables d'environnement

### 4.1 Objectif

Les informations sensibles sont fournies via des variables d'environnement.

Exemples :

- connexion SQL ;
- identifiants ;
- clés API ;
- certificats ;
- paramètres de sécurité.

---

### 4.2 Exemple

```text
APP_ENV=production

APP_PORT=8000

DATABASE_URL=...

SECRET_KEY=...

LOG_LEVEL=INFO
```

Le fichier `.env.example` documente les variables attendues.

---

## 5. Environnements

### 5.1 Développement

Caractéristiques :

- journalisation détaillée ;
- données de test ;
- outils de diagnostic activés.

---

### 5.2 Préproduction

Objectifs :

- validation complète ;
- performances proches de la production ;
- données représentatives.

---

### 5.3 Production

Caractéristiques :

- sécurité renforcée ;
- journalisation maîtrisée ;
- supervision permanente ;
- sauvegardes actives.

---

## 6. Chargement

Au démarrage de l'application :

1. lecture des variables d'environnement ;
2. chargement des fichiers de configuration ;
3. lecture des paramètres en base ;
4. validation ;
5. mise à disposition des composants.

En cas d'erreur, le démarrage est interrompu.

---

## 7. Validation

Chaque paramètre est contrôlé avant son utilisation.

Les contrôles portent notamment sur :

- présence ;
- type ;
- format ;
- plage de valeurs ;
- cohérence.

Une configuration invalide empêche le lancement de l'application.

---

## 8. Versionnement

Les fichiers de configuration non sensibles sont versionnés dans Git.

Les secrets ne sont jamais versionnés.

Chaque évolution importante est documentée.

---

## 9. Sécurité

Les secrets respectent les règles suivantes :

- stockage hors du dépôt Git ;
- accès limité ;
- rotation régulière ;
- journalisation des modifications.

Les mots de passe ne sont jamais stockés en clair.

---

## 10. Évolutivité

Le système de configuration permet d'ajouter facilement :

- de nouveaux paramètres ;
- de nouveaux environnements ;
- de nouveaux services ;
- de nouveaux modules.

Cette architecture garantit une configuration homogène et facilement maintenable sur l'ensemble de TurfIA.

---

# L027 — Conventions Git et gestion des versions

## 1. Objectif

### 1.1 Finalité

Ce document définit les règles de gestion du dépôt GitHub de TurfIA.

Il garantit :

- un historique clair ;
- des évolutions traçables ;
- des livraisons reproductibles ;
- une collaboration simplifiée.

Le dépôt GitHub constitue la référence unique du projet.

---

## 2. Organisation des branches

### 2.1 Branche principale

```text
main
```

Contient uniquement des versions validées et stables.

Aucun développement direct n'y est réalisé.

---

### 2.2 Branche de développement

```text
develop
```

Constitue la branche principale de travail.

Toutes les nouvelles fonctionnalités y sont intégrées après validation.

---

### 2.3 Branches de fonctionnalité

Les développements importants utilisent une branche dédiée.

Convention :

```text
feature/nom-fonctionnalite
```

Exemple :

```text
feature/api-statistiques

feature/dashboard

feature/import-pmu
```

---

## 3. Commits

### 3.1 Principes

Chaque commit est :

- atomique ;
- documenté ;
- facilement compréhensible.

Un commit ne traite qu'une seule évolution.

---

### 3.2 Format

Les messages utilisent la structure suivante :

```text
Type : Description
```

Exemples :

```text
feat : ajout du calcul TurfIA

fix : correction du calcul ROI

docs : ajout du livrable L021

refactor : simplification des services

test : ajout des tests API
```

---

## 4. Gestion des versions

Le projet adopte une numérotation de type :

```text
MAJEURE.MINEURE.CORRECTIF
```

Exemple :

```text
1.0.0

1.1.0

1.1.1
```

Les versions majeures correspondent à des évolutions incompatibles.

---

## 5. Tags Git

Chaque version publiée reçoit un tag.

Exemple :

```text
v1.0.0

v1.1.0

v2.0.0
```

Les tags correspondent à des versions livrables.

---

## 6. Documentation des versions

Chaque version est accompagnée d'une note de publication précisant :

- nouveautés ;
- corrections ;
- évolutions techniques ;
- migrations éventuelles.

---

## 7. Historique

L'historique Git constitue une source d'information essentielle.

Il permet :

- d'identifier l'origine d'une évolution ;
- de retrouver une version ;
- de comparer deux états du projet ;
- de faciliter les audits.

---

## 8. Bonnes pratiques

Les règles suivantes s'appliquent :

- commits fréquents ;
- messages explicites ;
- historique propre ;
- suppression des branches fusionnées ;
- documentation des évolutions importantes.

---

## 9. Évolutivité

Cette stratégie Git permet de faire évoluer TurfIA sur plusieurs années tout en conservant un historique lisible, documenté et parfaitement traçable.
# L020 — Stratégie de tests

## 1. Objectif

### 1.1 Finalité

La stratégie de tests définit les procédures permettant de vérifier le bon fonctionnement de TurfIA tout au long de son cycle de développement.

Elle poursuit les objectifs suivants :

- garantir la qualité du logiciel ;
- détecter rapidement les régressions ;
- sécuriser les évolutions ;
- fiabiliser les déploiements.

Les tests font partie intégrante du développement.

---

## 2. Principes

### 2.1 Automatisation

Chaque test automatisable doit être automatisé.

Les validations manuelles sont limitées aux contrôles visuels ou fonctionnels qui ne peuvent être automatisés.

---

### 2.2 Reproductibilité

Tous les tests doivent produire les mêmes résultats à partir d'un même jeu de données.

Les environnements de test sont isolés des environnements de production.

---

### 2.3 Indépendance

Chaque test doit pouvoir être exécuté indépendamment.

L'échec d'un test ne doit pas empêcher les autres de s'exécuter.

---

## 3. Organisation

```text
tests/

unit/

integration/

api/

database/

performance/

security/

fixtures/

reports/
```

Chaque catégorie répond à un objectif précis.

---

## 4. Tests unitaires

### 4.1 Objectif

Les tests unitaires vérifient individuellement les composants logiciels.

Ils concernent notamment :

- calculateurs ;
- services ;
- repositories ;
- utilitaires ;
- validations.

---

### 4.2 Règles

Chaque fonction métier importante possède au moins un test unitaire.

Les dépendances externes sont simulées.

Les tests sont rapides et déterministes.

---

## 5. Tests d'intégration

### 5.1 Objectif

Les tests d'intégration vérifient les interactions entre plusieurs composants.

Ils portent notamment sur :

- API ↔ Services ;
- Services ↔ Repositories ;
- Repositories ↔ Base SQL.

---

### 5.2 Jeux de données

Les données utilisées sont maîtrisées.

Chaque test initialise son propre environnement.

Aucun test ne dépend de données résiduelles.

---

## 6. Tests API

### 6.1 Objectif

Les tests API contrôlent :

- les routes ;
- les paramètres ;
- les réponses ;
- les codes HTTP ;
- les contrôles de sécurité.

---

### 6.2 Vérifications

Chaque route est testée pour :

- succès ;
- données invalides ;
- absence d'autorisation ;
- erreurs métier ;
- erreurs système.

---

## 7. Tests Base de données

### 7.1 Objectif

Ces tests vérifient :

- les migrations ;
- les contraintes ;
- les index ;
- les vues ;
- les performances des requêtes.

---

### 7.2 Intégrité

Les contrôles portent notamment sur :

- clés primaires ;
- clés étrangères ;
- contraintes CHECK ;
- contraintes UNIQUE.

---

## 8. Tests fonctionnels

### 8.1 Objectif

Les tests fonctionnels reproduisent les principaux scénarios utilisateurs.

Ils couvrent notamment :

- import d'une réunion ;
- pré-analyse ;
- analyse finale ;
- contrôle des résultats ;
- calcul du ROI ;
- génération d'un rapport.

---

### 8.2 Validation

Les résultats obtenus sont comparés aux résultats attendus.

Toute divergence est considérée comme une anomalie.

---

## 9. Tests de performance

### 9.1 Objectif

Les tests de performance mesurent :

- temps de réponse ;
- consommation mémoire ;
- charge processeur ;
- durée des traitements.

---

### 9.2 Indicateurs

Les principaux indicateurs suivis sont :

- analyse complète d'un Quinté ;
- import quotidien ;
- calcul des statistiques ;
- génération des tableaux de bord.

---

## 10. Tests de sécurité

### 10.1 Objectif

Les contrôles de sécurité portent notamment sur :

- authentification ;
- autorisations ;
- injections SQL ;
- validation des entrées ;
- gestion des sessions.

---

### 10.2 Confidentialité

Les tests vérifient que :

- les secrets restent protégés ;
- les informations sensibles ne sont jamais exposées ;
- les journaux respectent les règles de confidentialité.

---

## 11. Jeux de données

Les données de test sont conservées dans un répertoire dédié.

Elles comprennent notamment :

- réunions ;
- courses ;
- chevaux ;
- analyses ;
- statistiques.

Ces jeux de données permettent de reproduire tous les scénarios de validation.

---

## 12. Exécution

Les tests peuvent être exécutés :

- individuellement ;
- par catégorie ;
- sur l'ensemble du projet.

Ils sont intégrés à la chaîne CI/CD.

---

## 13. Rapports

Chaque campagne de tests produit un rapport comprenant :

- nombre de tests exécutés ;
- nombre de succès ;
- nombre d'échecs ;
- durée totale ;
- couverture fonctionnelle.

Ces rapports sont archivés.

---

## 14. Critères de validation

Une version est considérée comme valide lorsque :

- tous les tests critiques sont réussis ;
- aucune régression n'est détectée ;
- les performances restent conformes ;
- les exigences de sécurité sont satisfaites.

---

## 15. Amélioration continue

Chaque anomalie corrigée donne lieu à un nouveau test.

Ainsi, la couverture fonctionnelle augmente progressivement avec les évolutions de TurfIA.

La stratégie de tests constitue un élément essentiel de la qualité et de la fiabilité du projet.
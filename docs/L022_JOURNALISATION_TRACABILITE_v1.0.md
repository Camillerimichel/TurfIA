# L022 — Journalisation et traçabilité

## 1. Objectif

### 1.1 Finalité

La journalisation permet de conserver une trace fiable de l'ensemble des événements significatifs intervenant dans TurfIA.

Elle poursuit plusieurs objectifs :

- faciliter le diagnostic des anomalies ;
- assurer la traçabilité des traitements ;
- reconstituer une chronologie des événements ;
- produire des informations d'exploitation ;
- répondre aux besoins d'audit.

La journalisation est intégrée à tous les composants de la plateforme.

---

## 2. Principes

### 2.1 Journalisation centralisée

Tous les composants utilisent le même système de journalisation.

Les formats sont homogènes afin de permettre :

- les recherches ;
- les filtrages ;
- les statistiques ;
- la supervision.

---

### 2.2 Horodatage

Chaque événement est horodaté.

Les informations enregistrées comprennent notamment :

- date ;
- heure ;
- fuseau horaire ;
- durée éventuelle du traitement.

---

### 2.3 Niveaux

Les niveaux suivants sont utilisés.

| Niveau   | Description                    |
| -------- | ------------------------------ |
| DEBUG    | Diagnostic détaillé            |
| INFO     | Fonctionnement normal          |
| WARNING  | Situation inhabituelle         |
| ERROR    | Erreur empêchant un traitement |
| CRITICAL | Incident majeur                |

Le niveau DEBUG n'est activé qu'en développement.

---

## 3. Événements journalisés

### 3.1 Démarrage

Les événements suivants sont enregistrés :

- démarrage de l'application ;
- arrêt ;
- redémarrage ;
- version du logiciel ;
- environnement.

---

### 3.2 Authentification

Les informations suivantes sont enregistrées :

- connexion ;
- déconnexion ;
- échec d'authentification ;
- verrouillage éventuel.

Les mots de passe ne sont jamais enregistrés.

---

### 3.3 API

Chaque appel API génère un journal contenant :

- méthode HTTP ;
- ressource ;
- durée ;
- code retour ;
- utilisateur.

---

### 3.4 Base de données

Les événements suivants sont enregistrés :

- ouverture de session ;
- erreur SQL ;
- migration ;
- sauvegarde ;
- restauration.

Les requêtes SQL complètes ne sont pas enregistrées en production.

---

### 3.5 Automatisations

Chaque tâche planifiée produit un journal comprenant :

- nom ;
- date de lancement ;
- durée ;
- résultat ;
- message éventuel.

---

### 3.6 Analyses TurfIA

Les événements suivants sont historisés :

- début de pré-analyse ;
- analyse finale ;
- calcul du score ;
- génération des paris ;
- contrôle du ROI.

---

## 4. Structure d'un journal

Chaque entrée contient au minimum :

| Champ       | Description        |
| ----------- | ------------------ |
| Date        | Horodatage         |
| Niveau      | DEBUG, INFO...     |
| Module      | Composant concerné |
| Utilisateur | Si applicable      |
| Identifiant | Corrélation        |
| Message     | Description        |
| Durée       | Si disponible      |

---

## 5. Journalisation métier

Les traitements importants génèrent également des journaux fonctionnels.

Exemples :

- import d'une réunion ;
- création d'une analyse ;
- modification d'un paramètre ;
- recalcul statistique.

Ces événements permettent de suivre l'évolution du modèle TurfIA.

---

## 6. Rotation

Les journaux sont archivés régulièrement.

La politique de rotation repose notamment sur :

- la taille ;
- la durée de conservation ;
- le niveau de criticité.

Les archives sont compressées.

---

## 7. Conservation

La durée de conservation dépend de la nature des journaux.

| Type      | Conservation                   |
| --------- | ------------------------------ |
| Technique | Selon politique d'exploitation |
| Sécurité  | Selon politique de sécurité    |
| Métier    | Selon besoins du projet        |

Les durées exactes sont définies dans la politique d'exploitation.

---

## 8. Recherche

Le système de journalisation doit permettre :

- une recherche par date ;
- une recherche par utilisateur ;
- une recherche par course ;
- une recherche par analyse ;
- une recherche par identifiant de corrélation.

---

## 9. Corrélation

Chaque traitement possède un identifiant unique.

Cet identifiant est propagé :

- aux journaux API ;
- aux journaux SQL ;
- aux automatisations ;
- aux traitements métier.

Il permet de reconstituer l'intégralité d'un traitement.

---

## 10. Exploitation

Les journaux sont utilisés pour :

- le diagnostic ;
- la supervision ;
- les audits ;
- les statistiques ;
- l'amélioration continue.

Ils constituent un outil essentiel d'exploitation.

---

## 11. Confidentialité

Les journaux ne doivent jamais contenir :

- mots de passe ;
- secrets ;
- clés privées ;
- jetons d'authentification ;
- variables d'environnement.

Les informations confidentielles sont systématiquement masquées.

---

## 12. Évolutivité

Toute nouvelle fonctionnalité doit définir :

- les événements à journaliser ;
- leur niveau ;
- leur format ;
- leur durée de conservation.

La journalisation reste ainsi homogène sur l'ensemble du projet.
# L021 — Sécurité

## 1. Objectif

### 1.1 Finalité

La politique de sécurité de TurfIA définit l'ensemble des mesures destinées à garantir :

- la confidentialité des données ;
- l'intégrité des traitements ;
- la disponibilité de la plateforme ;
- la traçabilité des opérations ;
- la conformité réglementaire.

La sécurité est prise en compte dès la conception de chaque composant.

---

## 2. Principes fondamentaux

### 2.1 Security by Design

Chaque composant est développé en intégrant les exigences de sécurité dès sa conception.

Les mécanismes de protection ne doivent jamais être ajoutés uniquement après le développement.

---

### 2.2 Défense en profondeur

La protection repose sur plusieurs couches indépendantes :

```text
Internet

      │

Pare-feu

      │

Reverse Proxy

      │

API REST

      │

Services Métier

      │

Base SQL
```

La compromission d'une couche ne doit pas compromettre l'ensemble de la plateforme.

---

### 2.3 Principe du moindre privilège

Chaque utilisateur, processus ou service dispose uniquement des droits nécessaires à son fonctionnement.

Les privilèges excessifs sont interdits.

---

## 3. Authentification

### 3.1 Comptes utilisateurs

Chaque utilisateur possède un compte individuel.

Les comptes partagés sont interdits.

---

### 3.2 Politique des mots de passe

Les mots de passe doivent respecter une politique minimale de robustesse.

Ils sont :

- stockés sous forme hachée ;
- jamais enregistrés en clair ;
- jamais affichés.

---

### 3.3 Sessions

Les sessions disposent :

- d'une durée de validité limitée ;
- d'un mécanisme d'expiration ;
- d'une invalidation lors de la déconnexion.

---

## 4. Autorisations

### 4.1 Gestion des rôles

Les accès sont accordés selon un modèle RBAC.

Les principaux rôles sont :

| Rôle           | Description              |
| -------------- | ------------------------ |
| Administrateur | Gestion complète         |
| Analyste       | Analyses et statistiques |
| Consultation   | Lecture seule            |
| Automatisation | Services internes        |

---

### 4.2 Contrôle des accès

Chaque requête est contrôlée avant son exécution.

Les vérifications portent notamment sur :

- authentification ;
- rôle ;
- permissions ;
- contexte d'exécution.

---

## 5. Protection des données

### 5.1 Données sensibles

Les informations suivantes sont considérées comme sensibles :

- identifiants ;
- secrets ;
- clés d'API ;
- certificats ;
- paramètres de sécurité.

---

### 5.2 Chiffrement

Les données sensibles sont protégées :

- pendant leur stockage lorsque nécessaire ;
- pendant leur transmission ;
- pendant les sauvegardes.

---

## 6. Communications

Toutes les communications externes utilisent HTTPS.

Les communications internes peuvent être sécurisées selon l'architecture retenue.

Les protocoles obsolètes sont interdits.

---

## 7. Sécurité applicative

### 7.1 Validation des entrées

Toutes les données reçues sont validées avant traitement.

Les contrôles portent notamment sur :

- type ;
- format ;
- longueur ;
- plage de valeurs ;
- cohérence métier.

---

### 7.2 Injections

L'application protège contre :

- injections SQL ;
- injections de commandes ;
- injections HTML ;
- injections JavaScript.

Toutes les requêtes SQL utilisent des paramètres préparés.

---

### 7.3 Téléversements

Les fichiers importés sont contrôlés avant traitement.

Les vérifications portent notamment sur :

- format ;
- taille ;
- contenu ;
- nom du fichier.

---

## 8. Journalisation

### 8.1 Objectif

Les événements de sécurité sont journalisés.

Exemples :

- connexion ;
- déconnexion ;
- erreur d'authentification ;
- modification des paramètres ;
- lancement d'une automatisation ;
- erreur critique.

---

### 8.2 Confidentialité

Les journaux ne doivent jamais contenir :

- mots de passe ;
- clés privées ;
- secrets ;
- données confidentielles.

---

## 9. Sécurité de la base de données

Les accès SQL sont protégés par :

- comptes dédiés ;
- séparation des privilèges ;
- authentification ;
- journalisation ;
- sauvegardes régulières.

La base n'est jamais accessible directement depuis Internet.

---

## 10. Gestion des secrets

Les secrets sont stockés exclusivement dans :

- variables d'environnement ;
- coffre-fort de secrets si disponible.

Ils ne sont jamais :

- versionnés ;
- affichés ;
- enregistrés dans les journaux.

---

## 11. Supervision de sécurité

Les contrôles portent notamment sur :

- tentatives de connexion ;
- erreurs répétées ;
- indisponibilités ;
- modifications sensibles ;
- échecs de sauvegarde.

Les événements critiques déclenchent une alerte.

---

## 12. Gestion des vulnérabilités

Les dépendances sont régulièrement vérifiées.

Les mises à jour de sécurité sont appliquées selon leur niveau de criticité.

Les vulnérabilités identifiées sont corrigées dans les meilleurs délais.

---

## 13. Audit

Toutes les opérations importantes sont traçables.

Les audits permettent notamment de retrouver :

- l'auteur d'une action ;
- la date ;
- le contexte ;
- le résultat.

Les informations sont conservées selon la politique de rétention définie.

---

## 14. Reprise après compromission

En cas d'incident de sécurité, la procédure comprend notamment :

1. isolement du composant concerné ;
2. analyse de l'incident ;
3. restauration des données si nécessaire ;
4. renouvellement des secrets ;
5. validation du système ;
6. rédaction d'un rapport d'incident.

---

## 15. Évolutivité

La politique de sécurité est révisée à chaque évolution majeure de TurfIA.

Toute nouvelle fonctionnalité est soumise à une analyse de sécurité avant son intégration.

Cette politique constitue le référentiel de sécurité applicable à l'ensemble du projet.
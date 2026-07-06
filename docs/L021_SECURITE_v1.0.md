# L021 — Sécurité

## 0. Métadonnées du document

| Champ | Valeur |
| --- | --- |
| Identifiant | L021 |
| Niveau documentaire | Spécification technique (cf. L001 §3) |
| Version | 1.0 |
| Référentiel externe | OWASP Top 10, OWASP API Security Top 10 |
| Documents liés | L016 (architecture API REST), L034 (architecture sécurité, niveau SAD), L022 (journalisation) |

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

### 2.4 Correspondance avec OWASP Top 10

| Risque OWASP                              | Mesure TurfIA correspondante                  |
| -------------------------------------------- | -------------------------------------------------- |
| Contrôle d'accès défaillant                   | RBAC (§4), vérification systématique par requête (§4.2) |
| Défaillance cryptographique                    | Chiffrement des données sensibles (§5.2), HTTPS obligatoire (§6) |
| Injection                                        | Paramètres préparés systématiques (§7.2) |
| Conception non sécurisée                          | Security by Design (§2.1), analyse de sécurité avant intégration (§15) |
| Mauvaise configuration de sécurité                 | Configuration externalisée et revue (cf. L010, L026) |
| Composants vulnérables et obsolètes                 | Gestion des vulnérabilités et mises à jour (§12) |
| Identification et authentification défaillantes      | Politique de mots de passe et sessions (§3) |
| Journalisation et surveillance insuffisantes          | Journalisation systématique des événements de sécurité (§8), supervision (§11) |

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

### 7.2.1 Limitation de débit (rate limiting)

Les endpoints sensibles (authentification, écriture) appliquent une
limitation de débit par compte et par adresse IP source, afin de
limiter les attaques par force brute et les abus applicatifs. Les
seuils précis et leur ajustement relèvent de L034 (Architecture
sécurité, niveau SAD) afin d'éviter toute duplication de contenu.

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

### 14.1 Niveaux de sévérité d'incident

| Sévérité | Exemple                                              | Délai de réaction attendu |
| ---------- | ------------------------------------------------------- | ---------------------------- |
| Critique   | Compromission d'un compte administrateur, fuite de secrets | Immédiat (isolement sous quelques minutes) |
| Élevée     | Tentative d'intrusion détectée sans compromission avérée   | Sous quelques heures |
| Modérée    | Vulnérabilité identifiée sans exploitation constatée        | Selon criticité (§12) |

---

## 15. Évolutivité

La politique de sécurité est révisée à chaque évolution majeure de TurfIA.

Toute nouvelle fonctionnalité est soumise à une analyse de sécurité avant son intégration.

Cette politique constitue le référentiel de sécurité applicable à l'ensemble du projet.

---

## Historique

| Version | Description |
| --- | --- |
| 1.0 | Version initiale |
| 1.1 | Enrichissement industriel : métadonnées du document, correspondance avec OWASP Top 10, limitation de débit sur endpoints sensibles, niveaux de sévérité d'incident |

*Fin du document L021.*
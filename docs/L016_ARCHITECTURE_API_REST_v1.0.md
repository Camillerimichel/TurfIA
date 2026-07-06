# L016 — Architecture de l'API REST

## 0. Métadonnées du document

| Champ | Valeur |
| --- | --- |
| Identifiant | L016 |
| Niveau documentaire | Spécification technique (cf. L001 §3) |
| Version | 1.0 |
| Documents liés | L007/L032.x (architecture API du SAD), L021 (sécurité), L034 (architecture sécurité) |

## 1. Objectif

### 1.1 Finalité

L'API REST constitue le point d'entrée unique de TurfIA.

Toutes les communications entre les interfaces clientes et les traitements métier transitent exclusivement par cette API.

Elle garantit :

- l'unicité des traitements ;
- la cohérence des données ;
- la sécurité des accès ;
- la traçabilité des opérations.

Aucun accès direct à la base de données n'est autorisé depuis les interfaces clientes.

---

## 2. Principes d'architecture

### 2.1 Architecture en couches

```text
Client

      │

      ▼

API REST

      │

      ▼

Services Métier

      │

      ▼

Repositories

      │

      ▼

Base SQL
```

---

### 2.2 Principes

L'API respecte les principes suivants :

- architecture REST ;
- échanges JSON ;
- stateless ;
- versionnement ;
- validation systématique des données ;
- documentation automatique.

---

## 3. Organisation

### 3.1 Arborescence

```text
api/

routes/

schemas/

dependencies/

middlewares/

security/

errors/

documentation/
```

---

### 3.2 Routes

Chaque domaine métier possède son propre module.

Exemple :

```text
courses.py

chevaux.py

analyses.py

statistiques.py

paris.py

administration.py
```

---

### 3.3 Schémas

Les schémas décrivent :

- les entrées ;
- les sorties ;
- les validations.

Ils sont totalement indépendants des modèles SQL.

---

## 4. Ressources REST

### 4.1 Référentiels

```text
/hippodromes

/disciplines

/distances

/surfaces

/types-course
```

---

### 4.2 Courses

```text
/reunions

/courses

/partants

/resultats
```

---

### 4.3 Analyses

```text
/pre-analyses

/analyses

/selections

/paris
```

---

### 4.4 Statistiques

```text
/statistiques

/roi

/dashboard

/historique
```

---

### 4.5 Administration

```text
/configuration

/version

/supervision

/sante
```

---

## 5. Méthodes HTTP

Les méthodes utilisées sont les suivantes :

| Méthode | Utilisation                      |
| ------- | -------------------------------- |
| GET     | Consultation                     |
| POST    | Création                         |
| PUT     | Remplacement                     |
| PATCH   | Mise à jour partielle            |
| DELETE  | Suppression logique ou technique |

---

## 6. Réponses

### 6.1 Succès

Toutes les réponses retournent :

- code HTTP ;
- données ;
- horodatage ;
- version de l'API.

---

### 6.2 Erreurs

Les erreurs comportent systématiquement :

- code HTTP ;
- identifiant ;
- message ;
- description ;
- date ;
- identifiant de corrélation.

Les messages techniques internes ne sont jamais exposés au client.

---

## 7. Validation

Toutes les données reçues sont validées avant exécution des traitements.

Les contrôles portent notamment sur :

- types ;
- formats ;
- longueurs ;
- plages de valeurs ;
- cohérence métier.

Une requête invalide est rejetée avant toute écriture en base.

### 7.1 Emplacement de la validation

La validation de forme (types, formats, longueurs) est réalisée par les
schémas d'entrée au niveau des routes (module `schemas`). La validation
de cohérence métier (ex. une course référencée existe réellement) est
déléguée aux services (cf. L015 §7.2) et non dupliquée dans la couche
API.

---

## 8. Authentification

Toutes les opérations d'administration nécessitent une authentification.

Les principes retenus sont :

- authentification centralisée ;
- gestion des rôles ;
- expiration des sessions ;
- journalisation des accès.

---

## 9. Autorisations

Les autorisations sont gérées par rôle.

Exemples :

| Rôle           | Droits                   |
| -------------- | ------------------------ |
| Administrateur | Accès complet            |
| Analyste       | Analyses et statistiques |
| Consultation   | Lecture uniquement       |
| Automatisation | Services internes        |

Les droits sont vérifiés avant chaque traitement.

### 9.1 Principe du moindre privilège

Le rôle `Automatisation`, utilisé par les traitements planifiés (cf.
L017, L033), ne dispose que des droits strictement nécessaires à
l'exécution du workflow (cf. L005) : il ne dispose d'aucun droit
d'administration ni de suppression, même technique.

---

## 10. Journalisation

Chaque appel API produit un journal contenant notamment :

- date ;
- utilisateur ;
- ressource ;
- méthode ;
- durée ;
- code HTTP.

Les informations sensibles ne sont jamais enregistrées.

---

## 11. Documentation

La documentation de l'API est générée automatiquement.

Elle comprend :

- ressources ;
- paramètres ;
- schémas ;
- exemples ;
- codes d'erreur.

La documentation est synchronisée avec le code source.

---

## 12. Performances

Les objectifs de performance sont :

- temps de réponse prévisible ;
- limitation des traitements redondants ;
- pagination des listes volumineuses ;
- limitation des requêtes simultanées.

Les traitements longs sont délégués aux automatisations.

---

## 13. Versionnement

L'API est versionnée.

Toute évolution incompatible donne lieu à une nouvelle version.

Les anciennes versions restent disponibles pendant une période de transition définie.

---

## 14. Sécurité

Les mesures suivantes sont appliquées :

- HTTPS obligatoire ;
- validation des entrées ;
- limitation du débit des requêtes ;
- contrôle des droits ;
- protection contre les injections ;
- journalisation des accès.

La sécurité est appliquée de manière uniforme sur l'ensemble des ressources.

### 14.1 Renvoi vers les documents transverses de sécurité

Le détail des mécanismes d'authentification, de gestion des jetons, de
limitation de débit et de contrôles OWASP est spécifié en L021
(Sécurité) et L034 (Architecture sécurité) afin d'éviter toute
duplication de contenu susceptible de diverger.

---

## 15. Évolutivité

L'architecture permet l'ajout de nouvelles ressources REST sans remettre en cause les interfaces existantes.

Chaque nouveau module respecte les mêmes conventions de développement, de validation, de sécurité et de documentation.

Cette architecture constitue la référence officielle pour le développement de l'API REST de TurfIA.

---

## Historique

| Version | Description |
| --- | --- |
| 1.0 | Version initiale |
| 1.1 | Enrichissement industriel : métadonnées du document, emplacement de la validation (forme vs métier), principe du moindre privilège pour le rôle Automatisation, renvoi vers les documents transverses de sécurité |

*Fin du document L016.*
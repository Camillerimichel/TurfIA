# L007_API_v2.0.md --- Partie 2/3

# 5. Cycle de traitement d'une requête

Chaque requête suit un enchaînement identique afin de garantir un
comportement homogène.

``` mermaid
sequenceDiagram
participant C as Client
participant A as API
participant S as Services
participant M as Moteur
participant D as Base SQL

C->>A: Requête HTTP
A->>A: Validation
A->>S: Appel métier
S->>M: Traitement
M->>D: Lecture / Écriture
D-->>M: Données
M-->>S: Résultat
S-->>A: Réponse
A-->>C: JSON
```

## 5.1 Traitement des erreurs dans le cycle de requête

Toute erreur (validation, métier, technique) est interceptée par un
gestionnaire d'erreurs centralisé au niveau de l'API, qui la traduit en
réponse HTTP normalisée (cf. L032.1 §6, L023). Aucune exception
technique brute (trace Python, message SQL) n'est jamais renvoyée au
client.

# 6. Décisions d'architecture

## ADR-001 --- API unique

**Contexte** : plusieurs clients (interface web, futurs clients
mobiles/API tierces) doivent obtenir un comportement identique.
**Décision** : toutes les interfaces consomment les mêmes services
REST afin d'éviter les divergences de comportement.
**Conséquences** : aucune règle métier n'est dupliquée côté client ;
tout enrichissement d'affichage reste purement présentationnel.

## ADR-002 --- Versionnement

**Contexte** : l'API doit pouvoir évoluer sans casser les clients
existants.
**Décision** : toute évolution incompatible entraîne la création d'une
nouvelle version d'API (`/api/v2`, cf. L032.1 §4).
**Conséquences** : maintien temporaire de plusieurs versions en
parallèle, avec politique de dépréciation documentée en L039.

## ADR-003 --- Validation centralisée

**Contexte** : la cohérence des données ne doit pas dépendre de la
discipline de chaque client.
**Décision** : les contrôles de cohérence sont réalisés avant toute
exécution métier, au niveau de la couche API (schémas Pydantic).
**Conséquences** : toute règle de validation est documentée une seule
fois (cf. L009), évitant la duplication entre client et serveur.

## ADR-004 --- Absence d'état de session côté serveur

**Contexte** : la scalabilité et la simplicité opérationnelle sont
prioritaires.
**Décision** : l'API ne conserve aucun état de session en mémoire entre
deux requêtes ; l'authentification repose sur un jeton auto-porteur
(cf. L021, L034).
**Conséquences** : chaque requête doit contenir toutes les informations
nécessaires à son traitement.

# 7. Contraintes

L'API doit préserver :

-   la compatibilité des clients ;
-   des temps de réponse prévisibles ;
-   la traçabilité des appels ;
-   l'indépendance des services métier.

## 7.1 Politique de compatibilité ascendante

  Type de changement                          Impact                Action requise
  --------------------------------------------- ---------------------- --------------------------------
  Ajout d'un champ optionnel en réponse           Non cassant            Aucune, documentation mise à jour
  Ajout d'un endpoint                             Non cassant            Documentation OpenAPI mise à jour
  Suppression ou renommage d'un champ             Cassant                Nouvelle version d'API (`/api/v2`)
  Changement de sémantique d'un code HTTP         Cassant                Nouvelle version d'API + ADR

*Fin de la partie 2/3.*

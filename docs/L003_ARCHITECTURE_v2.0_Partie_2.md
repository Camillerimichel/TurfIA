# L003_ARCHITECTURE_v2.0.md --- Partie 2/3

# 5. Flux d'information

Les échanges entre composants suivent un principe de dépendance
unidirectionnelle. L'interface utilisateur ne dialogue jamais
directement avec la base de données. Toutes les opérations transitent
par l'API REST puis par les services métier.

``` mermaid
sequenceDiagram
participant UI as Interface
participant API as API REST
participant S as Services
participant E as Moteur TurfIA
participant DB as Base SQL

UI->>API: Requête
API->>S: Validation
S->>E: Exécution
E->>DB: Lecture / Écriture
DB-->>E: Données
E-->>S: Résultat
S-->>API: Réponse
API-->>UI: JSON
```

## 5.1 Gestion des erreurs dans le flux

En cas d'échec à une étape (validation, calcul, persistance), l'erreur
remonte selon une chaîne de responsabilité explicite plutôt que d'être
absorbée silencieusement :

``` mermaid
sequenceDiagram
participant API as API REST
participant S as Services
participant E as Moteur TurfIA
participant DB as Base SQL

API->>S: Requête
S->>E: Exécution
E->>DB: Écriture
DB--x E: Erreur (contrainte, timeout)
E--x S: Exception métier typée
S--x API: Erreur normalisée (cf. L023)
API--x API: Réponse HTTP d'erreur (cf. L007 format d'erreur)
```

Le détail des types d'exceptions et des codes d'erreur est défini en
L023 (Gestion des erreurs et exceptions).

# 6. Décisions architecturales (ADR)

## ADR-001 --- Architecture en couches

**Contexte** : besoin de séparer présentation, logique métier et
persistance pour limiter l'impact des évolutions technologiques.
**Décision** : la séparation en couches garantit l'indépendance entre
la présentation, les traitements métier et la persistance.
**Alternatives considérées** : architecture microservices (écartée,
cf. §1.1 Partie 1/3), architecture monolithique non structurée
(écartée pour risque de couplage fort).
**Conséquences** : nécessite une discipline de code (pas de logique
métier dans les routes ni dans les repositories) documentée en L015 et
L019.

## ADR-002 --- Services métier

**Contexte** : plusieurs points d'entrée (API, traitements planifiés)
doivent appliquer les mêmes règles métier.
**Décision** : toute logique métier est centralisée dans les services
afin d'éviter sa duplication dans les interfaces ou les API.
**Conséquences** : les services deviennent le point unique de test de
la logique métier (cf. L020).

## ADR-003 --- Référentiels indépendants

**Contexte** : les données de référence évoluent à un rythme différent
des données d'exploitation (courses, cotes, résultats).
**Décision** : les données de référence (chevaux, hippodromes,
entraîneurs, jockeys...) sont découplées des données d'exploitation
afin de faciliter leur évolution.
**Conséquences** : nécessite une gestion explicite des clés étrangères
et des règles de déduplication (cf. L004, L011, L030.x).

## ADR-004 --- Exécution planifiée via les mêmes services

**Contexte** : garantir un comportement identique entre exécution
interactive (API) et exécution automatisée (batch/scheduler).
**Décision** : les traitements planifiés invoquent les mêmes services
métier que les appels API, sans logique dupliquée (cf. §8).
**Conséquences** : les services doivent être exécutables hors contexte
HTTP (pas de dépendance implicite à la requête web).

# 7. Contraintes

L'architecture doit permettre :

-   l'ajout de nouveaux traitements ;
-   l'intégration de nouvelles sources de données ;
-   le maintien de la compatibilité des interfaces publiques ;
-   l'historisation complète des analyses.

## 7.1 Contraintes de conception dérivées

-   aucun accès direct à la base de données depuis l'interface ou un
    client externe : tout transite par l'API (cf. ADR-004 de L001) ;
-   aucune dépendance circulaire entre couches (Interface → API →
    Services → Moteur/Règles → Base), vérifiée par revue de code (cf.
    L019) ;
-   toute nouvelle dépendance externe (bibliothèque, service tiers)
    fait l'objet d'une justification documentée dans l'ADR
    correspondant.

*Fin de la partie 2/3.*

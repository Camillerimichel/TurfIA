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

# 6. Décisions architecturales (ADR)

## ADR-001 --- Architecture en couches

La séparation en couches garantit l'indépendance entre la présentation,
les traitements métier et la persistance.

## ADR-002 --- Services métier

Toute logique métier est centralisée dans les services afin d'éviter sa
duplication dans les interfaces ou les API.

## ADR-003 --- Référentiels indépendants

Les données de référence (chevaux, hippodromes, entraîneurs, jockeys...)
sont découplées des données d'exploitation afin de faciliter leur
évolution.

# 7. Contraintes

L'architecture doit permettre :

-   l'ajout de nouveaux traitements ;
-   l'intégration de nouvelles sources de données ;
-   le maintien de la compatibilité des interfaces publiques ;
-   l'historisation complète des analyses.

*Fin de la partie 2/3.*

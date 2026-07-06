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

# 6. Décisions d'architecture

## ADR-001 --- API unique

Toutes les interfaces consomment les mêmes services REST afin d'éviter
les divergences de comportement.

## ADR-002 --- Versionnement

Toute évolution incompatible entraîne la création d'une nouvelle version
d'API.

## ADR-003 --- Validation centralisée

Les contrôles de cohérence sont réalisés avant toute exécution métier.

# 7. Contraintes

L'API doit préserver :

-   la compatibilité des clients ;
-   des temps de réponse prévisibles ;
-   la traçabilité des appels ;
-   l'indépendance des services métier.

*Fin de la partie 2/3.*

# L008_BASE_SQL_v2.0.md --- Partie 2/3

# 5. Intégrité des données

L'architecture SQL garantit la cohérence des données au moyen de
contraintes relationnelles et de règles de gestion appliquées à chaque
domaine.

Les principes retenus sont :

-   clés primaires techniques sur chaque table ;
-   clés étrangères pour toutes les relations métier ;
-   contraintes d'unicité lorsque nécessaire ;
-   validation des données avant persistance ;
-   suppression logique privilégiée pour préserver l'historique.

``` mermaid
flowchart LR
Insert[Insertion] --> Validate[Validation]
Validate --> FK[Intégrité référentielle]
FK --> Persist[Persistance]
Persist --> History[Historisation]
```

# 6. Décisions d'architecture

## ADR-001 --- Historique immuable

Les données utilisées pour les analyses restent disponibles afin de
garantir la reproductibilité des résultats.

## ADR-002 --- Séparation des domaines

Les référentiels, les données métier et les données techniques sont
isolés afin de limiter les dépendances.

## ADR-003 --- Optimisation analytique

Les structures SQL sont conçues prioritairement pour les traitements de
lecture et d'analyse tout en conservant des performances d'écriture
satisfaisantes.

# 7. Contraintes

La structure relationnelle doit permettre :

-   l'ajout de nouvelles entités ;
-   l'évolution des indicateurs ;
-   le maintien de la compatibilité des traitements existants ;
-   des migrations maîtrisées.

*Fin de la partie 2/3.*

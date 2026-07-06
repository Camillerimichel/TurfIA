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

## 5.1 Suppression logique vs suppression physique

  Cas d'usage                          Type de suppression      Mécanisme
  -------------------------------------- -------------------------- ---------------------------
  Résultat d'analyse validé               Jamais supprimé            Immuabilité (ADR-001)
  Référentiel obsolète (ex. cheval retiré) Suppression logique        Colonne de statut / date de fin de validité
  Donnée technique temporaire (verrou)     Suppression physique       Purge planifiée (cf. L038)

# 6. Décisions d'architecture

## ADR-001 --- Historique immuable

**Contexte** : la reproductibilité des analyses exige que les données
ayant servi à un calcul restent accessibles telles quelles.
**Décision** : les données utilisées pour les analyses restent
disponibles afin de garantir la reproductibilité des résultats ; aucune
donnée d'analyse validée n'est mise à jour en place.
**Conséquences** : croissance continue du volume (cf. L038 pour la
stratégie d'archivage à long terme).

## ADR-002 --- Séparation des domaines

**Contexte** : les référentiels, les données métier et les données
techniques ont des cycles de vie et des besoins d'accès différents.
**Décision** : ils sont isolés afin de limiter les dépendances.
**Conséquences** : nécessite une gestion explicite des clés étrangères
inter-domaines et des conventions de nommage (cf. L011 §nommage).

## ADR-003 --- Optimisation analytique

**Contexte** : les besoins de lecture (statistiques, ROI historique)
sont fréquents et portent sur de gros volumes.
**Décision** : les structures SQL sont conçues prioritairement pour les
traitements de lecture et d'analyse tout en conservant des performances
d'écriture satisfaisantes.
**Conséquences** : usage de vues matérialisées ou d'index composites
(cf. L012, L024) là où le besoin est démontré, jamais par anticipation
spéculative.

## ADR-004 --- Transactions et niveau d'isolation

**Contexte** : plusieurs écritures concurrentes (collecte, calcul,
contrôle des résultats) peuvent viser les mêmes lignes.
**Décision** : le niveau d'isolation `READ COMMITTED` (défaut
PostgreSQL) est retenu, complété par des contraintes d'unicité et des
verrous applicatifs explicites lorsque nécessaire (cf. L005 §6.2).
**Conséquences** : les cas nécessitant une isolation plus stricte
doivent être identifiés et documentés explicitement plutôt que traités
par défaut en `SERIALIZABLE`, pour préserver la performance.

# 7. Contraintes

La structure relationnelle doit permettre :

-   l'ajout de nouvelles entités ;
-   l'évolution des indicateurs ;
-   le maintien de la compatibilité des traitements existants ;
-   des migrations maîtrisées.

## 7.1 Règles de nommage et de conception

-   noms de tables au pluriel, en minuscules avec underscores ;
-   clé primaire technique nommée `id` (entier ou UUID selon le
    domaine, cf. L011) ;
-   colonnes d'horodatage systématiques (`created_at`, `updated_at`)
    sur les tables mutables ;
-   toute contrainte métier significative est portée par une contrainte
    SQL (`CHECK`, `UNIQUE`, `FOREIGN KEY`) et non uniquement par le code
    applicatif, afin de garantir l'intégrité même en cas d'accès direct
    autorisé (outillage d'administration).

*Fin de la partie 2/3.*

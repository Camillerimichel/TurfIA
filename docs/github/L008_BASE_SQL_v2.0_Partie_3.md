# L008_BASE_SQL_v2.0.md --- Partie 3/3

# 8. Performances et évolutivité

L'architecture SQL est conçue pour conserver des performances constantes
malgré l'augmentation progressive du volume de données.

Les principaux leviers sont :

-   index adaptés aux principaux parcours de lecture ;
-   séparation des référentiels et des données historiques ;
-   historisation sans duplication inutile ;
-   optimisation des requêtes analytiques ;
-   préparation des futures migrations de schéma.

Les évolutions de structure doivent rester compatibles avec les
traitements existants et préserver l'intégrité des historiques.

# 9. Références

Ce document est complété par :

-   L004 : Modèle de données ;
-   L005 : Workflow ;
-   L006 : Algorithmes ;
-   L009 : Règles métier ;
-   L030 : Modèle relationnel détaillé.

## Historique

  Version   Description
  --------- ----------------------------------------------------
  1.0       Version initiale
  2.0       Réécriture orientée Software Architecture Document

*Fin du document L008.*

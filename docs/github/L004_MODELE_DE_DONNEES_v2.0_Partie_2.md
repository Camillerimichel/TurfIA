# L004_MODELE_DE_DONNEES_v2.0.md --- Partie 2/2

# 5. Contraintes de conception

Le modèle de données doit préserver l'intégrité des informations tout au
long du cycle de vie d'une analyse. Les mises à jour ne doivent jamais
modifier les historiques validés.

Les règles suivantes s'appliquent :

-   clés techniques sur toutes les entités ;
-   clés étrangères pour les relations ;
-   contraintes d'intégrité référentielle ;
-   versionnement des paramètres de calcul ;
-   historisation des analyses et résultats.

# 6. Évolutivité

L'architecture de données permet l'ajout de nouveaux référentiels,
indicateurs et sources sans remise en cause du schéma logique existant.

Les nouvelles entités doivent respecter les conventions de nommage et
les contrats définis pour les échanges entre composants.

# 7. Références

Ce document est complété par :

-   L008 : Architecture SQL ;
-   L005 : Workflow ;
-   L006 : Algorithmes ;
-   L009 : Règles métier ;
-   L030 : Modèle relationnel détaillé.

## Historique

  Version   Description
  --------- ----------------------------------------------------
  1.0       Version initiale
  2.0       Réécriture orientée Software Architecture Document

*Fin du document L004.*

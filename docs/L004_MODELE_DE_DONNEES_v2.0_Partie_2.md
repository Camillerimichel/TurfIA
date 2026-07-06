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

## 5.1 Règles de qualité des données

  Règle                                          Contrôle associé                    Document
  ----------------------------------------------- ------------------------------------- ------------------
  Un partant appartient à une course existante     Contrainte FK + validation applicative L011, L023
  Une cote est toujours rattachée à un horodatage  Colonne obligatoire, non nullable      L011, L030.3
  Un résultat ne peut être saisi avant la clôture   Règle métier appliquée en service       L009
  Aucune valeur de score hors intervalle défini     Contrainte CHECK + validation Pydantic  L006, L007

## 5.2 Stratégie de gestion des changements de schéma

Toute évolution du modèle logique est reflétée par une migration
versionnée (cf. L013) avant d'être documentée ici. Le modèle logique
(ce document) ne doit jamais diverger du schéma physique déployé :
toute divergence constatée est un défaut de gouvernance documentaire
(cf. L028).

# 6. Évolutivité

L'architecture de données permet l'ajout de nouveaux référentiels,
indicateurs et sources sans remise en cause du schéma logique existant.

Les nouvelles entités doivent respecter les conventions de nommage et
les contrats définis pour les échanges entre composants.

## 6.1 Risques et hypothèses

  Risque                                           Mitigation
  -------------------------------------------------- -------------------------------------------
  Croissance non maîtrisée du volume historique       Politique d'archivage définie en L038
  Incohérence entre référentiels de sources différentes  Règles de déduplication et de rapprochement (L009, L030.1)
  Ajout d'un domaine de données non anticipé           Revue d'architecture obligatoire avant migration (cf. L003 §10)

**Hypothèse** : le volume de données reste compatible avec un schéma
relationnel normalisé (3FN) sans dénormalisation massive à des fins de
performance ; toute dénormalisation ponctuelle est documentée comme
exception dans L011.

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
  2.1       Enrichissement industriel : classification des données, propriétaires fonctionnels, règles de qualité des données, stratégie de gestion des changements de schéma, risques et hypothèses

*Fin du document L004.*

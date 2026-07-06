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

## 8.1 Cibles mesurables

  Indicateur                                Cible                     Document de vérification
  ------------------------------------------- --------------------------- ---------------------------
  Temps de réponse d'une requête de lecture usuelle  < 100 ms (p95)         L024, L036
  Durée d'un batch quotidien complet          Cf. seuil défini en L036   L017, L033, L036
  Taux de tables sans index sur clé étrangère 0 %                        Revue de schéma (L011)

## 8.2 Stratégie de sauvegarde et de reprise

La disponibilité et l'intégrité de la base sont également garanties
par une politique de sauvegarde régulière et testée, détaillée en L038
(Sauvegarde et restauration). Ce document se limite à la structure
logique ; les procédures opérationnelles de sauvegarde n'y sont pas
dupliquées.

## 8.3 Risques et hypothèses

  Risque                                          Mitigation
  -------------------------------------------------- -----------------------------------
  Dégradation des performances avec la croissance du volume historique  Archivage/partitionnement à évaluer si seuils L036 dépassés
  Verrous prolongés lors de migrations sur tables volumineuses           Migrations conçues pour minimiser le verrouillage (cf. L013)

**Hypothèse** : les volumes restent, à moyen terme, compatibles avec
une instance PostgreSQL unique sans partitionnement natif ; cette
hypothèse est réévaluée annuellement (cf. L039).

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
  2.1       Enrichissement industriel : choix du SGBD justifié, isolation logique par schéma, suppression logique vs physique, ADR détaillées (dont transactions/isolation), règles de nommage, cibles mesurables, risques et hypothèses

*Fin du document L008.*

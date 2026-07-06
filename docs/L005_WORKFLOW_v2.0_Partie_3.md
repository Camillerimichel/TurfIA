# L005_WORKFLOW_v2.0.md --- Partie 3/3

# 8. Supervision des traitements

Chaque exécution produit un ensemble d'informations permettant d'assurer
la traçabilité complète :

-   identifiant d'exécution ;
-   date et heure de lancement ;
-   durée ;
-   statut ;
-   messages d'erreur éventuels ;
-   version des règles métier utilisées.

Ces informations alimentent les tableaux de bord d'exploitation.

## 8.1 Indicateurs de supervision (extrait)

  Indicateur                          Seuil d'alerte             Document
  ------------------------------------- --------------------------- ------------------
  Durée du traitement quotidien          > seuil défini en L036       L035, L036
  Nombre d'anomalies de validation        > seuil défini en L023       L023, L035
  Retard de disponibilité des résultats    Résultats absents à l'heure attendue L025, L035

# 9. Exigences non fonctionnelles

Le workflow doit garantir :

-   reproductibilité ;
-   auditabilité ;
-   performance constante ;
-   reprise après incident ;
-   indépendance vis-à-vis des interfaces.

## 9.1 Hypothèses et dépendances

-   le workflow suppose la disponibilité des référentiels avant le
    traitement d'une course (dépendance sur le domaine Référentiels de
    L004) ;
-   la fenêtre de collecte est supposée suffisante pour obtenir les
    données avant l'heure de départ ; tout dépassement est traité
    comme une exception (cf. §4.2) ;
-   aucune étape du workflow ne doit dépendre d'une ressource externe
    non versionnée (ex. calcul dépendant d'une API tierce sans
    fallback documenté).

# 10. Références

Le présent document est complété par :

-   L006 : Algorithmes ;
-   L007 : API ;
-   L008 : Base SQL ;
-   L009 : Règles métier ;
-   L033 : Traitements planifiés ;
-   L034 : Journalisation.

## Historique

  Version   Description
  --------- ----------------------------------------------------
  1.0       Version initiale
  2.0       Réécriture orientée Software Architecture Document
  2.1       Enrichissement industriel : entrées/sorties par étape, cas particuliers et exceptions, garanties d'idempotence, modes d'invocation, verrouillage/concurrence, politique de reprise, indicateurs de supervision

*Fin du document L005.*

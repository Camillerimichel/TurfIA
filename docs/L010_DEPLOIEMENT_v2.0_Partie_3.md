# L010_DEPLOIEMENT_v2.0.md --- Partie 3/3

# 8. Exploitation

Les procédures d'exploitation couvrent :

-   démarrage et arrêt des services ;
-   sauvegardes ;
-   restauration ;
-   supervision ;
-   rotation des journaux ;
-   mises à jour applicatives.

Chaque opération est documentée afin d'assurer la continuité de service.

## 8.1 Procédures d'exploitation courantes (renvoi)

Le détail opérationnel de chacune de ces procédures est spécifié dans
les documents transverses dédiés (L025 Exploitation/Administration,
L033 Traitements planifiés, L038 Sauvegarde et restauration) afin
d'éviter toute duplication de contenu susceptible de diverger.

# 9. Exigences non fonctionnelles

L'architecture de déploiement doit garantir :

-   disponibilité ;
-   résilience ;
-   sécurité ;
-   observabilité ;
-   maintenabilité.

Les mécanismes de surveillance et de journalisation permettent de
détecter rapidement les anomalies et de faciliter leur résolution.

## 9.1 Cibles mesurables

  Exigence      Indicateur                          Cible                Document
  --------------- ------------------------------------- -------------------- ------------------
  Disponibilité   Taux de disponibilité des services     ≥ 99 % (cf. L035, L025)
  Résilience       Temps de retour arrière (rollback)      < seuil défini en L025
  Sécurité          Secrets détectés en clair dans le dépôt  0 (cf. L021, L034)

# 10. Références

Le présent document est complété par :

-   L013 : Migrations SQL ;
-   L021 : Sécurité ;
-   L025 : Exploitation et administration ;
-   L026 : Gestion de la configuration ;
-   L033 : Traitements planifiés ;
-   L034 : Architecture sécurité ;
-   L035 : Architecture supervision ;
-   L036 : Architecture performances ;
-   L037 : Architecture journalisation ;
-   L038 : Sauvegarde et restauration.

## Historique

  Version   Description
  --------- ----------------------------------------------------
  1.0       Version initiale
  2.0       Réécriture orientée Software Architecture Document
  2.1       Enrichissement industriel : style de déploiement justifié, règles de progression entre environnements, classification des secrets, ADR détaillées (dont stratégie de rollback), critères de blocage de déploiement, cibles mesurables ; correction des références croisées L034-L038 pour cohérence avec la numérotation réelle du corpus

*Fin du document L010.*

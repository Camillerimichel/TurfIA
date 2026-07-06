# L003_ARCHITECTURE_v2.0.md --- Partie 3/3

# 8. Interactions entre composants

Chaque composant possède une responsabilité clairement définie. Les
échanges se font exclusivement par les interfaces publiques afin de
limiter les dépendances.

Les traitements planifiés utilisent les mêmes services métier que les
appels interactifs afin de garantir un comportement identique quel que
soit le mode d'exécution.

# 9. Exigences non fonctionnelles

L'architecture répond aux exigences suivantes :

-   maintenabilité ;
-   extensibilité ;
-   sécurité ;
-   performance prévisible ;
-   auditabilité ;
-   reproductibilité.

Toute évolution doit préserver ces propriétés.

# 10. Gouvernance d'architecture

Les évolutions suivent un processus documenté :

1.  analyse d'impact ;
2.  mise à jour des ADR ;
3.  évolution de la documentation ;
4.  implémentation ;
5.  validation technique ;
6.  mise en production.

# 11. Références

-   L004 : Modèle de données
-   L005 : Workflow
-   L006 : Algorithmes
-   L007 : API
-   L008 : Base SQL
-   L009 : Règles métier
-   L010 : Déploiement
-   L032.2 à L039 : Architecture transverse

## Historique

  Version   Description
  --------- ----------------------------------------------------
  1.0       Version initiale
  2.0       Réécriture orientée Software Architecture Document

*Fin du document L003.*

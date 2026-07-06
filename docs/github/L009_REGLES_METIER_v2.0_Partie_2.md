# L009_REGLES_METIER_v2.0.md --- Partie 2/2

# 5. Gouvernance des règles

Chaque règle métier est identifiée, documentée et versionnée. Toute
évolution fait l'objet d'une analyse d'impact avant son intégration afin
de préserver la comparabilité des analyses historiques.

Les règles sont appliquées exclusivement par les services métier et le
moteur TurfIA. Elles ne sont jamais implémentées dans l'interface
utilisateur ni directement dans l'API.

# 6. Contraintes

Les règles métier doivent garantir :

-   cohérence fonctionnelle ;
-   stabilité des traitements ;
-   auditabilité ;
-   explicabilité des décisions ;
-   indépendance vis-à-vis des technologies.

# 7. Références

Ce document est complété par :

-   L005 : Workflow ;
-   L006 : Algorithmes ;
-   L007 : API ;
-   L008 : Base SQL ;
-   L031 : Spécifications fonctionnelles détaillées.

## Historique

  Version   Description
  --------- ----------------------------------------------------
  1.0       Version initiale
  2.0       Réécriture orientée Software Architecture Document

*Fin du document L009.*

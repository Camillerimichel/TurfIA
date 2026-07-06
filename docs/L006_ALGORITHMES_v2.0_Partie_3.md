# L006_ALGORITHMES_v2.0.md --- Partie 3/3

# 8. Exigences non fonctionnelles

Le moteur d'analyse doit garantir :

-   des temps d'exécution prévisibles ;
-   une consommation maîtrisée des ressources ;
-   une reproductibilité complète ;
-   une traçabilité de chaque calcul ;
-   une évolutivité des modèles de scoring.

Toutes les optimisations doivent préserver les résultats fonctionnels.

# 9. Interactions

Le moteur d'analyse interagit avec :

-   les référentiels ;
-   les services métier ;
-   les règles métier ;
-   la base SQL ;
-   les traitements planifiés.

Il ne dialogue jamais directement avec l'interface utilisateur.

# 10. Références

Les mécanismes présentés sont détaillés dans :

-   L005 : Workflow ;
-   L007 : API ;
-   L008 : Base SQL ;
-   L009 : Règles métier ;
-   L031 : Spécifications algorithmiques.

## Historique

  Version   Description
  --------- ----------------------------------------------------
  1.0       Version initiale
  2.0       Réécriture orientée Software Architecture Document

*Fin du document L006.*

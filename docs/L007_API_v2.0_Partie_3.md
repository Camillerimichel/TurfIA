# L007_API_v2.0.md --- Partie 3/3

# 8. Sécurité

Les mécanismes de sécurité sont transverses à l'ensemble des services
exposés.

Ils comprennent notamment :

-   authentification des utilisateurs et des services ;
-   autorisation par rôle ;
-   validation des entrées ;
-   journalisation des appels ;
-   limitation des accès aux ressources sensibles.

La sécurité est appliquée avant toute exécution de logique métier.

# 9. Exigences non fonctionnelles

L'API doit garantir :

-   disponibilité ;
-   stabilité des contrats ;
-   compatibilité ascendante ;
-   performances constantes ;
-   observabilité ;
-   auditabilité.

Les traitements exposés ne doivent jamais dépendre de l'interface
cliente.

# 10. Références

Le présent document est complété par :

-   L032.2 : Ressources métier ;
-   L032.3 : Contrats REST ;
-   L005 : Workflow ;
-   L006 : Algorithmes ;
-   L008 : Base SQL.

## Historique

  Version   Description
  --------- ----------------------------------------------------
  1.0       Version initiale
  2.0       Réécriture orientée Software Architecture Document

*Fin du document L007.*

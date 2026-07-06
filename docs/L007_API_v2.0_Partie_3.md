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

## 8.1 Contrôles par catégorie de risque OWASP API Security

  Risque OWASP (API Security Top 10)      Contrôle appliqué                              Document
  ----------------------------------------- ------------------------------------------------ ------------------
  Autorisation défaillante au niveau objet   Vérification de propriété/rôle à chaque accès    L021, L034
  Authentification défaillante                Jetons signés, expiration, rotation              L021, L034
  Exposition excessive de données              Schémas de sortie explicites (pas de sérialisation brute) L007 §5, L032.x
  Absence de limitation de débit               Limitation de débit sur endpoints sensibles      L021, L024
  Mauvaise configuration de sécurité            Revue de configuration avant déploiement         L026, L034

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

## 9.1 Cibles mesurables

  Exigence         Indicateur                          Cible                Document
  ----------------- ------------------------------------- -------------------- ------------------
  Disponibilité      Taux de disponibilité mensuel         ≥ 99 % (cf. L025, L035)
  Performance         Temps de réponse p95                  < 300 ms (cf. L024, L036)
  Observabilité       Requêtes journalisées avec identifiant de corrélation 100 % (cf. L022, L037)

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
  2.1       Enrichissement industriel : niveau de maturité Richardson, audience par domaine, ADR détaillées, politique de compatibilité ascendante, contrôles OWASP API Security, cibles mesurables

*Fin du document L007.*

# L002_VISION_v2.0.md --- Partie 2/2

# 5. Périmètre fonctionnel

Le système couvre l'ensemble du cycle de vie d'une analyse hippique :

-   acquisition et validation des données ;
-   gestion des référentiels ;
-   pré-analyse ;
-   analyse finale ;
-   propositions de paris ;
-   contrôle des résultats ;
-   calcul du ROI ;
-   amélioration continue.

## 5.1 Hors périmètre fonctionnel

-   exécution ou intermédiation de paris réels ;
-   gestion de trésorerie ou de bankroll utilisateur ;
-   diffusion publique des analyses sans authentification (cf. L021).

# 6. Vision d'évolution

L'architecture est conçue pour intégrer de nouvelles sources de données,
de nouveaux indicateurs et de nouvelles méthodes de calcul sans remettre
en cause les résultats historiques.

Les évolutions sont pilotées par les Architecture Decision Records (ADR)
et documentées avant toute implémentation.

## 6.1 Trajectoire d'évolution envisagée

  Horizon        Évolution envisagée                                  Précondition
  --------------- ----------------------------------------------------- -------------------------------
  Court terme      Nouveaux indicateurs de risque (L031.3)              Historique suffisant validé
  Moyen terme       Extension à de nouvelles hippodromes/pays            Volumes compatibles avec L001 §2.1
  Long terme        Réévaluation du choix mono-base relationnelle (ADR-005 de L001) si la charge le justifie  Dépassement des seuils définis en L024/L036

Toute évolution de cette trajectoire fait l'objet d'un ADR dans L039
avant sa mise en œuvre.

# 7. Parties prenantes

-   utilisateurs métier ;
-   développeurs ;
-   architectes ;
-   exploitants ;
-   administrateurs.

Chaque population s'appuie sur un niveau documentaire spécifique afin de
limiter les dépendances entre architecture et implémentation.

## 7.1 Attentes par partie prenante

  Partie prenante     Attente vis-à-vis de la vision
  -------------------- --------------------------------------------------
  Utilisateur métier    Recommandations fiables, explicables et rapides à consulter
  Développeur            Vision stable évitant les réécritures fréquentes
  Architecte              Cohérence entre vision et décisions techniques réelles
  Exploitant              Vision compatible avec une exploitation simple et prévisible
  Administrateur          Visibilité sur la trajectoire d'évolution pour anticiper les besoins d'infrastructure

# 8. Critères de réussite

La plateforme est considérée conforme à sa vision lorsqu'elle garantit :

-   des analyses reproductibles ;
-   une traçabilité complète ;
-   des décisions explicables ;
-   une architecture modulaire ;
-   une amélioration continue mesurable par le ROI.

## 8.1 Risques pour la vision

  Risque                                                Impact sur la vision                 Mitigation
  ------------------------------------------------------ -------------------------------------- --------------------------
  Sur-optimisation du modèle sur données historiques      Perte de fiabilité en conditions réelles  Validation hors échantillon (L031.7)
  Dérive de périmètre (« scope creep »)                   Dilution de la philosophie « qualifier la course avant les chevaux » Revue de vision lors de chaque évolution majeure (L039)
  Dépendance à un nombre restreint de sources de données  Fragilité en cas de rupture de source     Diversification progressive documentée en L009/L010

# 9. Références

Le présent document est complété par :

-   L003 Architecture générale ;
-   L004 Modèle de données ;
-   L005 Workflow ;
-   L006 Algorithmes ;
-   L007 API ;
-   L008 Base SQL ;
-   L009 Règles métier ;
-   L010 Déploiement.

## Historique

  Version   Description
  --------- --------------------------------------------------------
  1.0       Première version
  2.0       Réécriture orientée Software Architecture Document
  2.1       Enrichissement industriel : non-objectifs, indicateurs mesurables, trajectoire d'évolution, risques pour la vision, attentes par partie prenante

*Fin du document L002.*

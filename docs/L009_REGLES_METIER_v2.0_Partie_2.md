# L009_REGLES_METIER_v2.0.md --- Partie 2/2

# 5. Gouvernance des règles

Chaque règle métier est identifiée, documentée et versionnée. Toute
évolution fait l'objet d'une analyse d'impact avant son intégration afin
de préserver la comparabilité des analyses historiques.

Les règles sont appliquées exclusivement par les services métier et le
moteur TurfIA. Elles ne sont jamais implémentées dans l'interface
utilisateur ni directement dans l'API.

## 5.1 Cycle de vie d'une règle métier

  Étape                Description                                       Responsable
  --------------------- --------------------------------------------------- --------------------
  Proposition            Identification d'un besoin ou d'une amélioration    Analyste métier
  Analyse d'impact        Évaluation de l'effet sur les analyses historiques  Architecte logiciel
  Versionnement           Attribution d'une nouvelle version de règles        Développeur
  Validation               Test de non-régression sur historique              Équipe projet (L020)
  Publication              Mise en production avec traçabilité                 Exploitant (L025)

## 5.2 Table de traçabilité (registre des règles)

Chaque règle métier significative est identifiée par un code stable
(ex. `RG-SCORING-001`) référencé dans le code, les tests et la
documentation L031.x correspondante, afin de permettre une recherche
croisée entre une décision historisée et la règle qui l'a produite (cf.
L022).

# 6. Contraintes

Les règles métier doivent garantir :

-   cohérence fonctionnelle ;
-   stabilité des traitements ;
-   auditabilité ;
-   explicabilité des décisions ;
-   indépendance vis-à-vis des technologies.

## 6.1 Principe d'explicabilité

Toute décision produite par une règle métier est accompagnée d'une
justification structurée (facteurs pris en compte, valeurs
intermédiaires) et non d'un simple résultat binaire. Ce principe
découle directement de la vision du produit (cf. L002 §4) et conditionne
la confiance de l'utilisateur métier dans la recommandation.

## 6.2 Risques et hypothèses

  Risque                                           Mitigation
  -------------------------------------------------- --------------------------------------
  Règle métier dupliquée entre deux services           Revue de code obligatoire (cf. L019)
  Changement de règle non accompagné de test de non-régression  Blocage en intégration continue (cf. L020)
  Ambiguïté entre règle métier et paramètre technique   Registre des règles explicite (§5.2)

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
  2.1       Enrichissement industriel : nature d'une règle métier (pureté fonctionnelle), exemples par domaine, cycle de vie d'une règle, registre de traçabilité, principe d'explicabilité, risques et hypothèses

*Fin du document L009.*

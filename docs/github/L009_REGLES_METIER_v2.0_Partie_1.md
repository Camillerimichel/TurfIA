# L009_REGLES_METIER_v2.0.md --- Partie 1/2

# 1. Objet

Ce document présente l'architecture des règles métier de TurfIA. Il
décrit leur rôle dans le système, leur organisation et les principes
permettant de garantir des décisions cohérentes, explicables et
reproductibles.

# 2. Principes

Les règles métier sont indépendantes de l'interface utilisateur, de
l'API et de la base de données. Elles constituent le référentiel
fonctionnel utilisé par le moteur d'analyse.

Les principes retenus sont :

-   centralisation des règles ;
-   paramétrage lorsque cela est pertinent ;
-   versionnement ;
-   traçabilité ;
-   reproductibilité.

# 3. Organisation

``` mermaid
flowchart LR
Data[Données] --> Rules[Règles métier]
Rules --> Engine[Moteur TurfIA]
Engine --> Decision[Décision]
Decision --> History[Historisation]
```

# 4. Domaines

  Domaine          Finalité
  ---------------- ----------------------
  Validation       Contrôle des données
  Qualification    Analyse de la course
  Scoring          Calcul des scores
  Recommandation   Sélection des paris
  Contrôle         Calcul du ROI

*Fin de la partie 1/2.*

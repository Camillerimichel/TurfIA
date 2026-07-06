# L005_WORKFLOW_v2.0.md --- Partie 1/3

# 1. Objet

Ce document décrit l'architecture fonctionnelle des traitements de
TurfIA. Il présente les différentes étapes du cycle de vie d'une analyse
ainsi que les interactions entre les composants applicatifs.

# 2. Principes

Le workflow est conçu pour être :

-   déterministe ;
-   entièrement traçable ;
-   rejouable ;
-   indépendant de l'interface utilisateur.

Chaque étape produit un état persistant permettant la reprise des
traitements.

# 3. Cycle global

``` mermaid
flowchart LR
A[Collecte] --> B[Validation]
B --> C[Pré-analyse]
C --> D[Analyse finale]
D --> E[Décision]
E --> F[Résultat]
F --> G[Contrôle ROI]
G --> H[Amélioration continue]
```

# 4. Étapes principales

  Étape            Objectif
  ---------------- -------------------------------------
  Collecte         Acquisition des données
  Validation       Contrôle de cohérence
  Pré-analyse      Qualification de la course
  Analyse finale   Classement et recommandations
  Contrôle         Comparaison aux résultats officiels

*Fin de la partie 1/3.*

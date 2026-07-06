# L002_VISION_v2.0.md --- Partie 1/2

# 1. Objet

Ce document présente la vision architecturale et fonctionnelle de
TurfIA. Il décrit les objectifs stratégiques du système, son périmètre,
les principes directeurs qui guident sa conception et les bénéfices
attendus pour les utilisateurs et les futurs développements.

# 2. Vision du produit

TurfIA est une plateforme d'aide à la décision dont la finalité est de
maximiser le retour sur investissement à long terme grâce à une approche
quantitative, reproductible et explicable.

Contrairement aux outils traditionnels orientés vers la prédiction de
l'arrivée, TurfIA cherche d'abord à qualifier la course avant de
qualifier les chevaux.

Cette philosophie structure l'ensemble de l'architecture.

# 3. Objectifs

-   centraliser les données nécessaires aux analyses ;
-   produire des décisions déterministes ;
-   conserver un historique complet ;
-   mesurer objectivement les performances ;
-   permettre une amélioration continue sans modifier les historiques.

# 4. Principes directeurs

  Principe           Description
  ------------------ -----------------------------------------
  Reproductibilité   Même entrée, même résultat
  Traçabilité        Chaque décision est historisée
  Modularité         Composants indépendants
  Explicabilité      Les recommandations sont justifiées
  Évolutivité        Les règles peuvent évoluer sans rupture

``` mermaid
flowchart LR
A[Sources] --> B[Collecte]
B --> C[Pré-analyse]
C --> D[Analyse finale]
D --> E[Contrôle]
E --> F[Historique]
F --> G[Amélioration continue]
```

*Fin de la partie 1/2.*

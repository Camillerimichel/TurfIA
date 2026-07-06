# L002_VISION_v2.0.md --- Partie 1/2

# 1. Objet

Ce document présente la vision architecturale et fonctionnelle de
TurfIA. Il décrit les objectifs stratégiques du système, son périmètre,
les principes directeurs qui guident sa conception et les bénéfices
attendus pour les utilisateurs et les futurs développements.

Ce document répond à la préoccupation (concern) « pourquoi ce système
existe-t-il et que doit-il garantir » au sens d'ISO/IEC/IEEE 42010. Il
précède logiquement L003 (comment le système est structuré) et ne doit
pas être confondu avec une spécification fonctionnelle détaillée.

# 2. Vision du produit

TurfIA est une plateforme d'aide à la décision dont la finalité est de
maximiser le retour sur investissement à long terme grâce à une approche
quantitative, reproductible et explicable.

Contrairement aux outils traditionnels orientés vers la prédiction de
l'arrivée, TurfIA cherche d'abord à qualifier la course avant de
qualifier les chevaux.

Cette philosophie structure l'ensemble de l'architecture.

## 2.1 Non-objectifs (hors périmètre de vision)

Afin d'éviter toute ambiguïté sur la portée du produit, les éléments
suivants sont explicitement exclus de la vision actuelle :

-   TurfIA n'est pas un service de paris (pas de flux financier direct,
    pas d'intégration à un opérateur de paris) ;
-   TurfIA ne garantit pas un gain systématique : il produit une
    estimation probabiliste du risque et du ROI théorique, pas une
    certitude ;
-   TurfIA ne vise pas, à ce stade, une couverture multi-pays ou
    multi-disciplines hippiques (cf. hypothèses L001 §2.1) ;
-   TurfIA n'automatise pas la prise de décision finale : l'utilisateur
    reste décisionnaire (cf. L009 Règles métier).

# 3. Objectifs

-   centraliser les données nécessaires aux analyses ;
-   produire des décisions déterministes ;
-   conserver un historique complet ;
-   mesurer objectivement les performances ;
-   permettre une amélioration continue sans modifier les historiques.

## 3.1 Objectifs mesurables (indicateurs de vision)

  Objectif                          Indicateur                                  Cible
  ---------------------------------- -------------------------------------------- -----------------------
  Centralisation des données          Part des sources intégrées via pipeline unique 100 %
  Décisions déterministes             Taux de résultats rejouables à l'identique   100 %
  Historique complet                  Analyses historisées vs analyses produites   100 %
  Mesure objective des performances   Fréquence de calcul du ROI réalisé          À chaque clôture de réunion
  Amélioration continue               Cycles d'évaluation méthodologique par an   ≥ 2 (cf. L031.7)

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

## 4.1 Justification des principes (rationale)

  Principe           Pourquoi ce principe est structurant
  ------------------ ------------------------------------------------------------
  Reproductibilité   Sans cela, aucune évaluation objective des performances n'est possible
  Traçabilité        Nécessaire pour l'audit et pour distinguer erreur humaine et erreur de méthode
  Modularité         Permet de faire évoluer le moteur de scoring sans casser l'API ni l'historique
  Explicabilité      Condition de confiance de l'utilisateur métier dans la recommandation
  Évolutivité        Garantit que l'ajout d'une règle métier ne nécessite pas de migration destructive

*Fin de la partie 1/2.*

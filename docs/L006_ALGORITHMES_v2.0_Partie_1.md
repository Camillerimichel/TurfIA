# L006_ALGORITHMES_v2.0.md --- Partie 1/3

# 1. Objet

Ce document présente l'architecture logique du moteur d'analyse de
TurfIA. Il décrit l'enchaînement des traitements, les responsabilités
des différents modules de calcul et les principes retenus pour garantir
des résultats déterministes et reproductibles.

Le détail mathématique et algorithmique de chaque module (formules,
pondérations, seuils) est spécifié dans la série L031.x ; ce document
se limite à l'architecture logique du moteur, indépendamment des
formules retenues.

# 2. Principes de conception

Le moteur d'analyse repose sur les principes suivants :

-   séparation entre données, règles métier et calculs ;
-   absence d'effets de bord ;
-   traitements déterministes ;
-   configuration externalisée des paramètres ;
-   historisation des versions de calcul.

# 3. Chaîne algorithmique

``` mermaid
flowchart LR
A[Données brutes] --> B[Validation]
B --> C[Normalisation]
C --> D[Calcul des indicateurs]
D --> E[Scoring]
E --> F[Classement]
F --> G[Recommandations]
G --> H[Historisation]
```

# 4. Modules

  Module           Responsabilité
  ---------------- ---------------------------------
  Validation       Contrôle des données
  Normalisation    Uniformisation des informations
  Indicateurs      Calcul des métriques
  Scoring          Évaluation des partants
  Classement       Hiérarchisation
  Recommandation   Génération des propositions

## 4.1 Contrats d'entrée/sortie par module

  Module            Entrée attendue                       Sortie produite                    Document de spécification
  ------------------ -------------------------------------- ------------------------------------ ----------------------------
  Validation          Données brutes normalisées             Données validées + rejets motivés   L009, L023
  Normalisation        Données validées                       Données normalisées (unités, formats) L030.x
  Indicateurs          Données normalisées + référentiels       Indicateurs bruts                  L031.1, L031.2
  Scoring              Indicateurs                             Score TurfIA par partant             L031.2
  Classement           Scores                                   Classement ordonné                  L031.6
  Recommandation       Classement + risque + ROI théorique       Proposition de pari                 L031.4, L031.5

## 4.2 Principe de composition

Chaque module est une fonction pure au sens fonctionnel : à entrée
identique, elle produit une sortie identique, sans lecture ni écriture
d'état partagé implicite. Cette propriété est la condition nécessaire
du déterminisme énoncé au §2 et est vérifiée par les tests de
non-régression décrits en L020.

*Fin de la partie 1/3.*

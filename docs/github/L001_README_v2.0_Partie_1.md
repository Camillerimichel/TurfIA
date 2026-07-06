# L001_README_v2.0.md --- Partie 1/3

## 1. Objet du document

Le présent document constitue le point d'entrée du Software Architecture
Document (SAD) de TurfIA. Il expose les principes d'architecture, les
objectifs de conception, les conventions documentaires et les décisions
structurantes qui gouvernent l'ensemble du projet.

Le SAD décrit **pourquoi** l'architecture est organisée de cette
manière. Les documents L011 à L032.1 décrivent **comment** chaque
composant est implémenté. Cette séparation est volontaire afin de
préserver la stabilité des choix d'architecture malgré les évolutions
technologiques.

## 2. Contexte

TurfIA est une plateforme d'analyse quantitative des courses hippiques.
Son objectif n'est pas uniquement de classer les chevaux mais de
déterminer, avant toute sélection, si une course présente une espérance
de gain suffisante pour justifier une prise de position.

Cette philosophie influence directement l'ensemble de l'architecture.

Les exigences majeures sont :

-   reproductibilité des calculs ;
-   historique immuable ;
-   décisions explicables ;
-   séparation des responsabilités ;
-   amélioration continue fondée exclusivement sur les résultats
    historiques.

## 3. Positionnement du Software Architecture Document

Le corpus documentaire est organisé en trois niveaux :

``` text
SAD
├── L001 à L010
├── L032.2 à L039
│
Spécifications techniques
├── L011 à L032.1
│
Documentation d'exploitation
```

Le présent document constitue la porte d'entrée de cette organisation
documentaire.

## 4. Principes fondateurs

### Modularité

Chaque composant possède une responsabilité unique.

### Faible couplage

Les composants communiquent uniquement via leurs interfaces publiques.

### Déterminisme

À données identiques, TurfIA doit toujours produire les mêmes résultats.

### Historisation

Aucune analyse validée n'est modifiée rétroactivement.

``` mermaid
flowchart LR
A[Sources] --> B[Collecte]
B --> C[Validation]
C --> D[Référentiels]
D --> E[Moteur TurfIA]
E --> F[Décision]
F --> G[Historisation]
```

*Fin de la partie 1/3.*

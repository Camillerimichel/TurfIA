# L005_WORKFLOW_v2.0.md --- Partie 1/3

# 1. Objet

Ce document décrit l'architecture fonctionnelle des traitements de
TurfIA. Il présente les différentes étapes du cycle de vie d'une analyse
ainsi que les interactions entre les composants applicatifs.

Ce document constitue la **vue de processus** du SAD au sens
ISO/IEC/IEEE 42010 : il répond à la préoccupation « comment les données
circulent-elles et se transforment-elles dans le temps », par
opposition à L003 (vue logique statique) et L004 (vue informationnelle).

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

## 4.1 Entrées, sorties et critères de sortie par étape

  Étape            Entrée                          Sortie                            Critère de passage à l'étape suivante
  ---------------- -------------------------------- ---------------------------------- --------------------------------------
  Collecte          Sources externes (L009/L010)     Données brutes normalisées          Aucune erreur de format bloquante
  Validation        Données brutes normalisées        Données validées ou rejetées        100 % des enregistrements contrôlés
  Pré-analyse       Données validées                  Qualification de la course          Score de qualification calculé
  Analyse finale     Qualification + référentiels       Classement, score, recommandation   Décision déterministe produite
  Contrôle           Résultats officiels                Écart prédiction/réalité, ROI réel   Résultat officiel disponible

## 4.2 Cas particuliers et exceptions

-   **course annulée** : le workflow s'arrête après la collecte, l'état
    est historisé avec un statut explicite (« annulée ») plutôt que
    supprimé ;
-   **donnée manquante non bloquante** (ex. cote provisoire) : le
    traitement se poursuit avec un indicateur de confiance réduit,
    documenté en L006 ;
-   **donnée manquante bloquante** (ex. partants absents) : le
    traitement est interrompu et journalisé comme anomalie (cf. L023).

*Fin de la partie 1/3.*

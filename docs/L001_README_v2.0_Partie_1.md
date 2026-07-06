# L001_README_v2.0.md --- Partie 1/3

## 0. Métadonnées du document

  Champ                    Valeur
  ------------------------ ---------------------------------------------
  Identifiant               L001
  Titre                     README --- Point d'entrée du SAD
  Version                   2.0
  Statut                    Approuvé
  Norme de référence        ISO/IEC/IEEE 42010:2011 (Architecture description)
  Propriétaire              Architecte logiciel TurfIA
  Public visé               Équipe de développement, exploitation, gouvernance, auditeurs
  Documents dépendants      Tous les documents L002 à L039
  Fréquence de révision     À chaque évolution structurante de l'architecture

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

### 1.1 Conformité à ISO/IEC/IEEE 42010

Le SAD de TurfIA suit les principes de la norme ISO/IEC/IEEE 42010
relative à la description d'architecture des systèmes et logiciels.
Cette norme structure une description d'architecture (AD) autour des
notions suivantes, reprises tout au long du corpus documentaire :

-   **Parties prenantes (stakeholders)** : personnes ou rôles ayant un
    intérêt dans le système (cf. §1.2) ;
-   **Préoccupations (concerns)** : sujets d'intérêt des parties
    prenantes vis-à-vis du système (performance, sécurité, coût,
    évolutivité, etc.) ;
-   **Points de vue (viewpoints)** : conventions de construction d'une
    vue permettant d'adresser un ensemble de préoccupations ;
-   **Vues (views)** : représentations du système du point de vue d'un
    ensemble de préoccupations (diagrammes Mermaid, modèles de
    données, schémas d'API) ;
-   **Justification (rationale)** : motivation des choix
    d'architecture, documentée sous forme d'ADR (cf. §7 de la partie
    2/3).

Chaque document du SAD précise, lorsque cela est pertinent, à quel(s)
point(s) de vue il correspond (fonctionnel, informationnel, processus,
déploiement, sécurité).

### 1.2 Parties prenantes et préoccupations

  Partie prenante              Préoccupation principale
  ----------------------------- ------------------------------------------
  Architecte logiciel           Cohérence, dette technique, évolutivité
  Développeur                   Clarté des contrats, testabilité
  Exploitant / Ops              Supervision, procédures de reprise, alerting
  Responsable sécurité          Confidentialité, intégrité, traçabilité
  Analyste métier / Turfiste    Fiabilité des résultats, explicabilité
  Gouvernance projet            Auditabilité, conformité, gestion du risque
  Futur mainteneur              Documentation à jour, compréhensibilité

### 1.3 Comment lire ce document

Ce document (L001) doit être lu en premier. Il ne contient aucune
règle métier ni détail d'implémentation : ceux-ci sont réservés aux
documents référencés au §10 de la partie 3/3. Toute contradiction
apparente entre un document technique et le présent document doit être
signalée et traitée comme un défaut de gouvernance documentaire (cf.
L028).

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

### 2.1 Hypothèses structurantes

-   les sources de données externes (résultats, cotes, partants) sont
    disponibles selon une fréquence connue et documentée en L009/L010
    (collecte) ;
-   le volume de données (un pays de courses hippiques) reste
    compatible avec une architecture mono-base relationnelle (cf.
    L011) sans sharding horizontal ;
-   l'équipe projet reste de taille réduite, ce qui justifie une
    architecture modulaire mais non un découpage en microservices ;
-   l'exploitation est assurée par la même équipe qui développe,
    supprimant le besoin d'une organisation SRE dédiée à ce stade.

### 2.2 Dépendances externes majeures

  Dépendance                     Nature                     Impact en cas d'indisponibilité
  ------------------------------- -------------------------- ---------------------------------
  Fournisseurs de données courses  Source de données          Blocage de la collecte du jour
  Base de données PostgreSQL       Infrastructure             Indisponibilité totale du service
  Environnement d'exécution Python Plateforme d'exécution     Arrêt des traitements planifiés
  Dépôt Git (GitHub)                Gouvernance / traçabilité  Perte de capacité de déploiement

### 2.3 Risques architecturaux identifiés

  Risque                                          Probabilité   Impact   Mitigation
  ------------------------------------------------ ------------ -------- -----------------------------------
  Changement de format d'une source de données      Moyenne      Élevé    Couche de validation/adaptation (L009/L023)
  Dérive du schéma de données sans migration tracée Faible       Élevé    Migrations versionnées (L013)
  Sur-couplage entre moteur et API                  Moyenne      Moyen    Séparation stricte Services/Repositories (L015/L016)
  Perte d'historique par erreur d'exploitation      Faible       Critique Sauvegardes et historisation immuable (L038, ADR-002)

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

### Testabilité

Chaque composant expose des interfaces permettant un test unitaire ou
d'intégration sans dépendance sur l'infrastructure de production (cf.
L020 Stratégie de tests).

### Sécurité par conception

Les contrôles de sécurité (authentification, validation des entrées,
moindre privilège) sont intégrés dès la conception des composants et
non ajoutés a posteriori (cf. L021, L034).

### Observabilité

Chaque composant produit des journaux, métriques et traces exploitables
permettant de comprendre son comportement en production sans accès
direct au code (cf. L022, L035, L037).

``` mermaid
flowchart LR
A[Sources] --> B[Collecte]
B --> C[Validation]
C --> D[Référentiels]
D --> E[Moteur TurfIA]
E --> F[Décision]
F --> G[Historisation]
```

### 4.1 Attributs de qualité et cibles mesurables

Conformément à ISO/IEC 25010, les principes ci-dessus se traduisent en
attributs de qualité mesurables, détaillés et suivis dans les documents
techniques correspondants :

  Attribut de qualité      Cible indicative                         Document de référence
  ------------------------ ----------------------------------------- ------------------------
  Reproductibilité          100 % des analyses rejouables à l'identique  L006, L009
  Disponibilité             Traitements quotidiens critiques ≥ 99 %   L025, L035
  Temps de réponse API       p95 < 300 ms sur les endpoints de lecture L007, L032.2, L036
  Auditabilité               100 % des décisions tracées et horodatées L022, L037
  Maintenabilité             Couverture de tests ≥ 80 % sur le cœur métier L020

*Fin de la partie 1/3.*

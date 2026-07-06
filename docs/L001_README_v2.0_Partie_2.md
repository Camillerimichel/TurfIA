# L001_README_v2.0.md --- Partie 2/3

## 5. Objectifs architecturaux

L'architecture de TurfIA poursuit plusieurs objectifs structurants :

-   garantir une séparation claire entre les données, les règles métier
    et les algorithmes ;
-   permettre l'évolution indépendante des composants ;
-   assurer la reproductibilité complète des traitements ;
-   faciliter les tests, l'audit et la maintenance ;
-   permettre l'ajout de nouveaux algorithmes de scoring sans
    régression sur les analyses historiques déjà publiées ;
-   limiter le coût d'exploitation en conservant une infrastructure
    simple et proportionnée aux volumes réels de données.

Chaque décision d'architecture est prise afin de préserver ces
propriétés sur le long terme. Les compromis (« trade-offs ») entre ces
objectifs, lorsqu'ils existent, sont documentés explicitement dans les
ADR (§7) plutôt que résolus implicitement dans le code.

## 6. Organisation des composants

L'application est organisée autour des domaines suivants :

-   Acquisition des données ;
-   Référentiels ;
-   Moteur d'analyse ;
-   Règles métier ;
-   Persistance ;
-   API REST ;
-   Interface utilisateur ;
-   Supervision et traitements planifiés.

``` mermaid
flowchart TD
UI[Interface] --> API
API --> Services
Services --> Engine[Moteur TurfIA]
Engine --> Rules[Règles métier]
Engine --> DB[(Base SQL)]
Scheduler[Tâches planifiées] --> Services
```

### 6.1 Responsabilités par domaine

  Domaine                        Responsabilité                                          Document de référence
  ------------------------------- -------------------------------------------------------- -----------------------
  Acquisition des données          Collecte, normalisation, contrôle qualité des sources     L009, L010
  Référentiels                     Gestion des données stables (chevaux, jockeys, hippodromes) L004, L011, L030.x
  Moteur d'analyse                 Calcul du score TurfIA, du risque, du ROI théorique       L006, L031.x
  Règles métier                    Application des règles de sélection et de classement      L009, L031.6
  Persistance                      Stockage relationnel, vues, migrations                    L008, L011-L013
  API REST                         Exposition des services métier aux clients                L007, L016, L032.x
  Interface utilisateur            Présentation, saisie, restitution des analyses            L018
  Supervision / traitements planifiés  Orchestration batch, alerting, reprise sur incident   L017, L033, L035

## 7. Décisions d'architecture (ADR)

Les ADR ci-dessous constituent les décisions structurantes du SAD. Elles
suivent un format condensé (contexte / décision / conséquences) et sont
complétées par des ADR spécifiques dans les documents techniques
concernés lorsque la décision est locale à un composant.

### ADR-001 --- Modularité

**Contexte** : une plateforme d'analyse évolutive nécessite d'ajouter
de nouveaux algorithmes et sources sans réécrire l'existant.
**Décision** : les fonctionnalités sont réparties en composants
spécialisés afin de limiter les dépendances.
**Conséquences** : plus de fichiers/modules à maintenir, mais
isolation des régressions et tests ciblés possibles.

### ADR-002 --- Historique immuable

**Contexte** : la crédibilité du système repose sur la possibilité de
vérifier a posteriori la pertinence de ses prédictions.
**Décision** : les analyses validées ne sont jamais modifiées. Toute
évolution méthodologique produit une nouvelle version et conserve les
résultats historiques.
**Conséquences** : croissance continue du volume de données
historisées ; nécessité d'une stratégie de purge/archivage à long
terme (cf. L038).

### ADR-003 --- Déterminisme

**Contexte** : la confiance dans les résultats exige leur
reproductibilité.
**Décision** : les calculs ne doivent dépendre que des données
disponibles au moment de l'analyse et de la version des règles
utilisée.
**Conséquences** : interdiction d'utiliser des sources d'aléa non
tracées (horloge système, générateurs aléatoires non contrôlés) dans
le moteur de scoring.

### ADR-004 --- API découplée

**Contexte** : plusieurs clients (interface web, futurs clients
mobiles, outils d'administration) doivent consommer les mêmes
services métier.
**Décision** : toute interaction avec les services métier passe par
des interfaces stables afin de préserver l'indépendance des clients.
**Conséquences** : nécessité d'un versionnement explicite de l'API
(cf. L032.1 §4).

### ADR-005 --- Base de données relationnelle unique

**Contexte** : les volumes de données restent compatibles avec un
moteur relationnel unique et les besoins d'intégrité référentielle
sont forts (courses, partants, cotes, résultats).
**Décision** : PostgreSQL est retenu comme unique système de
persistance transactionnelle, sans introduction d'un second système de
stockage (NoSQL, cache distribué) tant que le besoin n'est pas
démontré.
**Conséquences** : simplicité opérationnelle ; réévaluation nécessaire
si le volume ou la charge dépassent les seuils définis en L024/L036.

## 8. Contraintes non fonctionnelles

Les exigences prioritaires sont :

-   maintenabilité ;
-   évolutivité ;
-   sécurité ;
-   auditabilité ;
-   performances prévisibles ;
-   facilité d'exploitation.

### 8.1 Contraintes techniques imposées

-   langage principal : Python (services, moteur, automatisations) ;
-   base de données : PostgreSQL, schéma versionné par migrations
    (L013) ;
-   API : REST/JSON, documentée en OpenAPI (L007, L032.x) ;
-   hébergement : environnement unique de production, sans
    distribution multi-région à ce stade (cf. L010) ;
-   gestion de version : Git, avec convention de branches et de
    messages de commit définie en L027.

### 8.2 Contraintes organisationnelles

-   toute modification de l'architecture est documentée avant sa mise
    en œuvre (cf. L028 Gouvernance projet) ;
-   les décisions non documentées ne sont pas considérées comme des
    décisions d'architecture engageantes ;
-   la charge de maintenance documentaire est répartie au fil de l'eau
    plutôt que différée en fin de projet.

*Fin de la partie 2/3.*

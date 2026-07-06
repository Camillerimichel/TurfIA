# L003_ARCHITECTURE_v2.0.md --- Partie 1/3

# 1. Objet

Ce document présente l'architecture générale de TurfIA. Il décrit les
composants fonctionnels, leurs responsabilités, leurs interactions et
les principes de conception retenus afin de garantir une plateforme
modulaire, maintenable et évolutive.

# 2. Principes architecturaux

L'architecture repose sur plusieurs principes :

-   séparation stricte des responsabilités ;
-   faible couplage entre composants ;
-   forte cohésion fonctionnelle ;
-   interfaces stables ;
-   traitement déterministe ;
-   historisation complète.

# 3. Vue logique

``` mermaid
flowchart LR
UI[Interface Web]
API[API REST]
SERV[Services métier]
ENGINE[Moteur TurfIA]
RULES[Règles métier]
DB[(Base SQL)]

UI --> API
API --> SERV
SERV --> ENGINE
ENGINE --> RULES
ENGINE --> DB
```

# 4. Responsabilités des composants

  Composant       Responsabilité
  --------------- --------------------------------
  Interface       Consultation et administration
  API             Point d'accès unique
  Services        Orchestration métier
  Moteur TurfIA   Calcul des scores
  Règles métier   Validation des décisions
  Base SQL        Persistance et historique

*Fin de la partie 1/3.*

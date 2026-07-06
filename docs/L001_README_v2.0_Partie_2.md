# L001_README_v2.0.md --- Partie 2/3

## 5. Objectifs architecturaux

L'architecture de TurfIA poursuit plusieurs objectifs structurants :

-   garantir une séparation claire entre les données, les règles métier
    et les algorithmes ;
-   permettre l'évolution indépendante des composants ;
-   assurer la reproductibilité complète des traitements ;
-   faciliter les tests, l'audit et la maintenance.

Chaque décision d'architecture est prise afin de préserver ces
propriétés sur le long terme.

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

## 7. Décisions d'architecture (ADR)

### ADR-001 --- Modularité

Les fonctionnalités sont réparties en composants spécialisés afin de
limiter les dépendances.

### ADR-002 --- Historique immuable

Les analyses validées ne sont jamais modifiées. Toute évolution
méthodologique produit une nouvelle version et conserve les résultats
historiques.

### ADR-003 --- Déterminisme

Les calculs ne doivent dépendre que des données disponibles au moment de
l'analyse et de la version des règles utilisée.

### ADR-004 --- API découplée

Toute interaction avec les services métier passe par des interfaces
stables afin de préserver l'indépendance des clients.

## 8. Contraintes non fonctionnelles

Les exigences prioritaires sont :

-   maintenabilité ;
-   évolutivité ;
-   sécurité ;
-   auditabilité ;
-   performances prévisibles ;
-   facilité d'exploitation.

*Fin de la partie 2/3.*

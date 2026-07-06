# L003_ARCHITECTURE_v2.0.md --- Partie 1/3

# 1. Objet

Ce document présente l'architecture générale de TurfIA. Il décrit les
composants fonctionnels, leurs responsabilités, leurs interactions et
les principes de conception retenus afin de garantir une plateforme
modulaire, maintenable et évolutive.

## 1.1 Style architectural retenu

TurfIA adopte une **architecture en couches (layered architecture)**
combinée à une séparation **hexagonale légère** entre le domaine métier
(moteur, règles) et ses adaptateurs (API, persistance). Ce choix est
préféré à une architecture microservices pour les raisons suivantes :

-   la taille de l'équipe et le volume de données ne justifient pas le
    coût opérationnel d'un système distribué (cf. L001 §2.1) ;
-   le déterminisme et la cohérence transactionnelle sont plus simples
    à garantir dans un processus unique adossé à une base
    relationnelle unique ;
-   la modularité recherchée est obtenue par des frontières de modules
    internes (packages Python) plutôt que par des frontières réseau.

Ce choix est réévalué si les seuils de charge définis en L024/L036 sont
dépassés (cf. ADR-005 de L001).

## 1.2 Vues fournies par ce document

Conformément à ISO/IEC/IEEE 42010, ce document fournit trois vues
principales : une **vue logique** (§3), une **vue de flux/processus**
(L003 Partie 2/3 §5) et une **vue des interactions** (Partie 3/3 §8).
La vue de déploiement est traitée séparément en L010.

# 2. Principes architecturaux

L'architecture repose sur plusieurs principes :

-   séparation stricte des responsabilités ;
-   faible couplage entre composants ;
-   forte cohésion fonctionnelle ;
-   interfaces stables ;
-   traitement déterministe ;
-   historisation complète.

## 2.1 Scénarios d'attribut de qualité (quality attribute scenarios)

  Attribut       Scénario                                                            Réponse attendue
  -------------- --------------------------------------------------------------------- ---------------------------------------
  Modifiabilité   Ajouter un nouvel indicateur de scoring                              Aucune modification de l'API ni de la base historique
  Performance     Pic de consultation lors de l'ouverture des paris                    p95 < 300 ms (cf. L024, L036)
  Disponibilité   Panne d'une source de données externe                                Dégradation contrôlée, pas d'arrêt total (cf. L023)
  Sécurité        Tentative d'accès non authentifié à une route d'administration       Rejet en 401/403, journalisé (cf. L021, L034)
  Testabilité     Modification du moteur de scoring                                    Suite de tests de non-régression sur historique rejouable (cf. L020)

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

## 4.1 Contrats d'interface entre composants

  Interface                         Fournisseur    Consommateur     Nature du contrat
  ---------------------------------- -------------- ---------------- ----------------------------------
  API REST (`/api/v1/*`)              API            Interface, tiers  Contrat OpenAPI versionné (L007, L032.x)
  Interface Services ↔ Moteur         Moteur TurfIA  Services          Appels de fonctions Python typées, sans effet de bord caché
  Interface Services ↔ Règles métier  Règles métier  Services          Fonctions pures de validation, retour explicite (accepté/rejeté + motif)
  Interface Moteur/Services ↔ Base    Repositories   Moteur, Services  Requêtes SQL paramétrées, aucun SQL dynamique en clair (cf. L021)

## 4.2 Ce que ce document ne couvre pas

Le détail des schémas de tables, des endpoints ou des règles de gestion
n'est pas traité ici : il relève respectivement de L011 (schéma SQL),
L007/L032.x (API) et L009 (règles métier). Ce document se limite à la
structure et aux responsabilités de haut niveau.

*Fin de la partie 1/3.*

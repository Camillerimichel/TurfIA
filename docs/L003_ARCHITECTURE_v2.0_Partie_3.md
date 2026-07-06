# L003_ARCHITECTURE_v2.0.md --- Partie 3/3

# 8. Interactions entre composants

Chaque composant possède une responsabilité clairement définie. Les
échanges se font exclusivement par les interfaces publiques afin de
limiter les dépendances.

Les traitements planifiés utilisent les mêmes services métier que les
appels interactifs afin de garantir un comportement identique quel que
soit le mode d'exécution.

## 8.1 Matrice des interactions

  Composant source   Composant cible   Synchrone / Asynchrone   Document détaillant l'interaction
  ------------------- ----------------- ------------------------- -------------------------------------
  Interface            API               Synchrone (HTTP)          L007, L018, L032.x
  API                  Services          Synchrone (appel interne) L016
  Scheduler             Services          Asynchrone (planifié)     L017, L033
  Services              Moteur TurfIA     Synchrone                 L006, L031.x
  Moteur TurfIA         Base SQL          Synchrone (transactionnel) L008, L011

# 9. Exigences non fonctionnelles

L'architecture répond aux exigences suivantes :

-   maintenabilité ;
-   extensibilité ;
-   sécurité ;
-   performance prévisible ;
-   auditabilité ;
-   reproductibilité.

Toute évolution doit préserver ces propriétés.

## 9.1 Cibles mesurables

  Exigence         Indicateur                                   Cible                Document de vérification
  ----------------- --------------------------------------------- -------------------- ---------------------------
  Performance        Temps de réponse p95 des endpoints de lecture < 300 ms             L024, L036
  Auditabilité        Taux de décisions historisées avec horodatage 100 %               L022, L037
  Sécurité            Taux de routes sensibles couvertes par authentification 100 %      L021, L034
  Reproductibilité    Taux d'analyses rejouables à l'identique      100 %                L006, L020

## 9.2 Hypothèses et limites de l'architecture actuelle

-   l'architecture suppose une charge concurrente modérée (usage par
    une équipe restreinte, pas de trafic public massif) ;
-   la montée en charge horizontale n'est pas traitée par ce document :
    elle relève d'une évolution architecturale documentée en L039 si
    nécessaire ;
-   la disponibilité multi-région n'est pas un objectif actuel (cf.
    L001 §2.1).

# 10. Gouvernance d'architecture

Les évolutions suivent un processus documenté :

1.  analyse d'impact ;
2.  mise à jour des ADR ;
3.  évolution de la documentation ;
4.  implémentation ;
5.  validation technique ;
6.  mise en production.

## 10.1 RACI simplifié du processus d'évolution architecturale

  Étape                Responsable (R)      Approbateur (A)      Consulté (C)        Informé (I)
  --------------------- --------------------- --------------------- -------------------- --------------------
  Analyse d'impact       Développeur           Architecte logiciel   Exploitant           Gouvernance (L028)
  Mise à jour des ADR    Architecte logiciel   Propriétaire du SAD   Développeur          Équipe projet
  Implémentation         Développeur           Architecte logiciel   —                    Exploitant
  Validation technique   Architecte logiciel   Propriétaire du SAD   Développeur          Gouvernance (L028)
  Mise en production     Exploitant            Architecte logiciel   Développeur          Équipe projet

## 10.2 Critères de rejet d'une évolution

Une évolution proposée est rejetée ou renvoyée en revue si elle :

-   introduit un couplage direct entre l'interface et la base de
    données ;
-   modifie rétroactivement un résultat historisé (violation de
    l'ADR-002 de L001) ;
-   n'est pas accompagnée d'une mise à jour de la documentation
    concernée ;
-   dégrade un indicateur mesurable défini en §9.1 sans justification
    documentée.

# 11. Références

-   L004 : Modèle de données
-   L005 : Workflow
-   L006 : Algorithmes
-   L007 : API
-   L008 : Base SQL
-   L009 : Règles métier
-   L010 : Déploiement
-   L032.2 à L039 : Architecture transverse

## Historique

  Version   Description
  --------- ----------------------------------------------------
  1.0       Version initiale
  2.0       Réécriture orientée Software Architecture Document
  2.1       Enrichissement industriel : style architectural justifié, scénarios d'attributs de qualité, contrats d'interface, ADR détaillées, matrice des interactions, RACI de gouvernance

*Fin du document L003.*

# L017 --- Architecture des automatisations v1.0

## 0. Métadonnées du document

| Champ | Valeur |
| --- | --- |
| Identifiant | L017 |
| Niveau documentaire | Spécification technique (cf. L001 §3) |
| Version | 1.0 |
| Documents liés | L005 (workflow), L033 (architecture traitements planifiés), L035 (supervision), L025 (exploitation) |

## 1. Objectif

Ce document décrit l'architecture des traitements automatiques de
TurfIA.

Les automatisations permettent d'exécuter sans intervention humaine
l'ensemble des traitements quotidiens nécessaires au fonctionnement du
moteur d'analyse, au suivi des résultats et à l'amélioration continue du
modèle.

------------------------------------------------------------------------

# 2. Principes

Les automatisations reposent sur les principes suivants :

-   exécution entièrement autonome ;
-   traitements idempotents ;
-   journalisation complète ;
-   reprise après incident ;
-   absence de dépendance aux interfaces utilisateur.

Chaque tâche est indépendante et peut être relancée sans altérer les
données.

## 2.1 Verrouillage et exécution concurrente

Chaque tâche acquiert un verrou applicatif nominatif (nom de la tâche +
date métier concernée) avant exécution. Toute tentative d'exécution
concurrente de la même tâche est rejetée et journalisée comme
avertissement plutôt que mise en attente silencieuse, conformément à
L005 §6.2.

------------------------------------------------------------------------

# 3. Architecture générale

``` text
                Scheduler
                     │
                     ▼
        Gestionnaire de tâches
                     │
     ┌───────────────┼────────────────┐
     ▼               ▼                ▼
Pré-analyse     Analyse finale   Contrôle ROI
     │               │                │
     └───────────────┼────────────────┘
                     ▼
           Calcul des statistiques
                     │
                     ▼
           Mise à jour historique
                     │
                     ▼
               Sauvegarde
```

------------------------------------------------------------------------

# 4. Tâches automatiques

## 4.1 Pré-analyse quotidienne

Déclenchement : tous les jours à 06h00.

Actions :

-   récupération des réunions ;
-   récupération des partants ;
-   récupération des cotes ;
-   calcul des indicateurs ;
-   génération de la pré-analyse ;
-   archivage.

## 4.2 Analyse finale

Déclenchement : 30 minutes avant le départ officiel.

Actions :

-   actualisation des cotes ;
-   prise en compte des non-partants ;
-   recalcul du Score TurfIA ;
-   recalcul du risque ;
-   recalcul du ROI théorique ;
-   génération des paris.

## 4.3 Contrôle des résultats

Déclenchement : tous les jours à 09h00.

Actions :

-   récupération de l'arrivée officielle ;
-   récupération des rapports ;
-   calcul du ROI ;
-   mise à jour des statistiques.

## 4.4 Calcul des statistiques

Déclenchement : après chaque contrôle.

Actions :

-   mise à jour des statistiques globales ;
-   statistiques par hippodrome ;
-   statistiques par type de pari ;
-   statistiques par score.

## 4.5 Sauvegarde

Déclenchement : quotidien.

Actions :

-   sauvegarde SQL ;
-   sauvegarde des journaux ;
-   vérification d'intégrité.

## 4.6 Tolérance aux pannes par tâche

| Tâche                  | Tolérance à un échec                                  |
| ------------------------ | -------------------------------------------------------- |
| Pré-analyse quotidienne    | Nouvelle tentative automatique bornée (cf. L005 §7.1) ; alerte si échec persistant |
| Analyse finale             | Critique : alerte immédiate, aucune dégradation silencieuse acceptée (fenêtre temporelle courte) |
| Contrôle des résultats      | Nouvelle tentative différée si la source de résultats n'est pas encore disponible |
| Calcul des statistiques      | Rejoué au prochain cycle si échec, sans impact sur les analyses |
| Sauvegarde                    | Alerte immédiate ; absence de sauvegarde ne bloque pas l'exploitation du jour mais est un incident de sévérité élevée (cf. L038) |

------------------------------------------------------------------------

# 5. Gestionnaire des tâches

Chaque tâche possède :

-   identifiant ;
-   nom ;
-   catégorie ;
-   date de début ;
-   date de fin ;
-   durée ;
-   statut ;
-   journal associé.

------------------------------------------------------------------------

# 6. Gestion des erreurs

Chaque automatisation applique :

-   journalisation systématique ;
-   arrêt contrôlé ;
-   reprise automatique lorsque possible ;
-   notification des erreurs critiques.

------------------------------------------------------------------------

# 7. Priorités

Ordre d'exécution :

1.  Pré-analyse
2.  Analyse finale
3.  Contrôle des résultats
4.  Statistiques
5.  Sauvegardes

------------------------------------------------------------------------

# 8. Supervision

Indicateurs :

-   nombre de tâches ;
-   durée moyenne ;
-   taux de réussite ;
-   nombre d'échecs ;
-   disponibilité des services.

## 8.1 Seuils d'alerte indicatifs

| Indicateur                         | Seuil d'alerte                          |
| ------------------------------------- | ------------------------------------------ |
| Retard de démarrage d'une tâche planifiée | > seuil défini en L035                      |
| Taux d'échec d'une tâche sur 7 jours    | > seuil défini en L035                      |
| Absence de sauvegarde depuis N jours    | Alerte immédiate (cf. L038)                |

------------------------------------------------------------------------

# 9. Évolutivité

De nouvelles tâches pourront être ajoutées sans modifier les traitements
existants.

Toute nouvelle tâche planifiée définit explicitement : son
déclencheur, sa tolérance aux pannes (cf. §4.6), son verrou applicatif
(cf. §2.1) et les indicateurs de supervision associés (cf. §8), avant
sa mise en production.

------------------------------------------------------------------------

# 10. Conclusion

Les automatisations constituent le cœur opérationnel de TurfIA et
garantissent l'exécution fiable, répétable et traçable des traitements
quotidiens.

------------------------------------------------------------------------

## Historique

| Version | Description |
| --- | --- |
| 1.0 | Version initiale |
| 1.1 | Enrichissement industriel : métadonnées du document, verrouillage et exécution concurrente, tolérance aux pannes par tâche, seuils d'alerte indicatifs, critères d'ajout d'une nouvelle tâche |

*Fin du document L017.*

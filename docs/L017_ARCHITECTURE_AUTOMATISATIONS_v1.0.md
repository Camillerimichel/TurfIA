# L017 --- Architecture des automatisations v1.0

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

------------------------------------------------------------------------

# 9. Évolutivité

De nouvelles tâches pourront être ajoutées sans modifier les traitements
existants.

------------------------------------------------------------------------

# 10. Conclusion

Les automatisations constituent le cœur opérationnel de TurfIA et
garantissent l'exécution fiable, répétable et traçable des traitements
quotidiens.

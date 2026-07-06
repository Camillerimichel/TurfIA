# L005_WORKFLOW_v2.0.md --- Partie 2/3

# 5. Transitions d'état

Chaque étape du workflow constitue un état stable. Une transition n'est
autorisée que lorsque les contrôles de cohérence de l'étape précédente
sont validés.

Les traitements sont idempotents : une même opération peut être relancée
sans modifier le résultat final.

``` mermaid
stateDiagram-v2
[*] --> Collecte
Collecte --> Validation
Validation --> PréAnalyse
PréAnalyse --> AnalyseFinale
AnalyseFinale --> Historisation
Historisation --> Contrôle
Contrôle --> Statistiques
Statistiques --> [*]
```

## 5.1 Garanties d'idempotence

L'idempotence est assurée par les mécanismes suivants :

-   clé métier stable (identifiant course/partant/date) utilisée comme
    contrainte d'unicité en base (cf. L011) ;
-   opérations d'écriture en « upsert » contrôlé plutôt qu'en insertion
    aveugle ;
-   aucune dépendance à un état en mémoire non persisté entre deux
    exécutions.

# 6. Orchestration

Les traitements sont pilotés par les services métier. Les interfaces
utilisateur, les tâches planifiées et les API REST utilisent tous la
même chaîne d'orchestration afin de garantir un comportement identique.

## 6.1 Modes d'invocation du workflow

  Mode d'invocation      Déclencheur                         Document de référence
  ----------------------- ------------------------------------ ------------------------
  Interactif               Requête API authentifiée             L007, L032.x
  Planifié                 Ordonnanceur (cron / scheduler)       L017, L033
  Manuel (administration)   Action d'un opérateur via l'interface L018, L025

## 6.2 Verrouillage et concurrence

Afin d'éviter l'exécution concurrente d'un même traitement (ex. deux
lancements du batch quotidien), un verrou applicatif est acquis pour la
durée du traitement (cf. L017, L033). Toute tentative concurrente est
rejetée explicitement et journalisée plutôt que mise en file d'attente
silencieuse.

# 7. Gestion des erreurs

Une anomalie interrompt uniquement le traitement concerné. Les journaux
permettent la reprise à partir du dernier état validé sans retraiter les
étapes précédentes.

## 7.1 Politique de reprise

  Type d'erreur                 Comportement                                  Document
  ------------------------------ ---------------------------------------------- ------------------
  Erreur transitoire (réseau)     Nouvelle tentative avec backoff borné          L023, L024
  Erreur de données (validation)  Rejet de l'enregistrement, poursuite du reste  L009, L023
  Erreur bloquante (schéma, config) Arrêt du traitement, alerte à l'exploitation L023, L025, L035

*Fin de la partie 2/3.*

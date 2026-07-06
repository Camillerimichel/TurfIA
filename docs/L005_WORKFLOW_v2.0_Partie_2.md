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

# 6. Orchestration

Les traitements sont pilotés par les services métier. Les interfaces
utilisateur, les tâches planifiées et les API REST utilisent tous la
même chaîne d'orchestration afin de garantir un comportement identique.

# 7. Gestion des erreurs

Une anomalie interrompt uniquement le traitement concerné. Les journaux
permettent la reprise à partir du dernier état validé sans retraiter les
étapes précédentes.

*Fin de la partie 2/3.*

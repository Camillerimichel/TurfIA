# L010_DEPLOIEMENT_v2.0.md --- Partie 1/3

# 1. Objet

Ce document décrit l'architecture de déploiement de TurfIA. Il présente
les environnements d'exécution, les composants déployés, les principes
de configuration et les exigences garantissant la reproductibilité des
installations.

# 2. Principes

Le déploiement repose sur les principes suivants :

-   séparation stricte des environnements ;
-   configuration externalisée ;
-   automatisation des installations ;
-   reproductibilité ;
-   sécurité des secrets.

# 3. Vue d'ensemble

``` mermaid
flowchart LR
Client --> ReverseProxy
ReverseProxy --> API
API --> Services
Services --> Database[(SQL)]
Services --> Scheduler[Tâches planifiées]
```

# 4. Environnements

  Environnement   Finalité
  --------------- -------------------------------
  Développement   Conception et tests unitaires
  Intégration     Validation technique
  Recette         Validation fonctionnelle
  Production      Exploitation

*Fin de la partie 1/3.*

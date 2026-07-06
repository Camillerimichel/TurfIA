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

## 2.1 Style de déploiement retenu

Le déploiement s'appuie sur un processus reproductible fondé sur des
scripts et fichiers de configuration versionnés (« infrastructure as
code » au sens large), sans imposer un orchestrateur de conteneurs
complet tant que l'échelle de l'infrastructure ne le justifie pas (cf.
L001 §2.1). Ce choix privilégie la simplicité opérationnelle pour une
équipe restreinte plutôt que l'exhaustivité d'outillage.

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

## 4.1 Règles de progression entre environnements

Aucune version applicative n'accède à la production sans avoir
préalablement franchi, dans l'ordre, les environnements de
développement, intégration et recette. Chaque passage d'environnement
est conditionné par la réussite des contrôles définis en L020 (stratégie
de tests) et documenté dans l'historique de déploiement (cf. L025).

## 4.2 Isolation des environnements

Les environnements ne partagent ni base de données, ni secrets, ni
configuration. Un incident ou une erreur de manipulation en recette ne
peut donc pas affecter la production.

*Fin de la partie 1/3.*

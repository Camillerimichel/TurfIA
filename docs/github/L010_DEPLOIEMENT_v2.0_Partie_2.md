# L010_DEPLOIEMENT_v2.0.md --- Partie 2/3

# 5. Configuration

Toutes les configurations sont externalisées afin de séparer le code
applicatif des paramètres d'exploitation.

Les éléments suivants sont configurables :

-   connexions aux bases de données ;
-   paramètres de sécurité ;
-   variables d'environnement ;
-   planification des traitements ;
-   journalisation ;
-   paramètres applicatifs.

Les secrets ne sont jamais stockés dans le code source.

``` mermaid
flowchart LR
Config[Fichiers de configuration]
Secrets[Secrets]
Env[Variables d'environnement]

Config --> Services
Secrets --> Services
Env --> Services
```

# 6. Décisions d'architecture

## ADR-001 --- Configuration externalisée

Toutes les valeurs spécifiques aux environnements sont extraites du
code.

## ADR-002 --- Déploiement reproductible

Une même version applicative produit un comportement identique dans tous
les environnements sous réserve d'une configuration adaptée.

## ADR-003 --- Automatisation

Les procédures de déploiement doivent être automatisables afin de
réduire les risques d'erreur humaine.

# 7. Contraintes

Le déploiement doit garantir :

-   disponibilité des services ;
-   sécurité des secrets ;
-   simplicité des mises à jour ;
-   possibilité de retour arrière.

*Fin de la partie 2/3.*

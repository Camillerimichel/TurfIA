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

## 5.1 Classification et gestion des secrets

  Type de secret                Mécanisme de stockage                  Rotation
  ------------------------------- ---------------------------------------- -----------------
  Identifiants de base de données  Variables d'environnement / gestionnaire de secrets  Sur incident ou périodiquement (cf. L021)
  Clés de signature de jetons       Gestionnaire de secrets, hors dépôt Git   Périodique (cf. L034)
  Identifiants de sources externes  Gestionnaire de secrets                  Sur changement contractuel

Aucun secret n'est commité dans le dépôt Git, y compris dans
l'historique (cf. L027, L021).

# 6. Décisions d'architecture

## ADR-001 --- Configuration externalisée

**Contexte** : une même version du code doit pouvoir s'exécuter dans
plusieurs environnements sans modification.
**Décision** : toutes les valeurs spécifiques aux environnements sont
extraites du code (cf. L026).
**Conséquences** : nécessite une validation systématique de la
configuration au démarrage (fail-fast en cas de configuration
incomplète).

## ADR-002 --- Déploiement reproductible

**Contexte** : la confiance dans une mise en production repose sur sa
prévisibilité.
**Décision** : une même version applicative produit un comportement
identique dans tous les environnements sous réserve d'une configuration
adaptée.
**Conséquences** : toute divergence de comportement entre environnements
est traitée comme un défaut de configuration, jamais comme une
variation acceptable.

## ADR-003 --- Automatisation

**Contexte** : les déploiements manuels sont une source majeure
d'erreurs opérationnelles.
**Décision** : les procédures de déploiement doivent être
automatisables afin de réduire les risques d'erreur humaine.
**Conséquences** : toute étape manuelle documentée est considérée comme
temporaire, en attente d'automatisation (cf. L025).

## ADR-004 --- Stratégie de retour arrière (rollback)

**Contexte** : une mise en production peut révéler un défaut non détecté
en recette.
**Décision** : chaque déploiement conserve la version précédente
disponible et documente une procédure de retour arrière explicite.
**Conséquences** : les migrations de schéma (cf. L013) doivent être
conçues, autant que possible, pour rester compatibles avec la version
précédente le temps du déploiement.

# 7. Contraintes

Le déploiement doit garantir :

-   disponibilité des services ;
-   sécurité des secrets ;
-   simplicité des mises à jour ;
-   possibilité de retour arrière.

## 7.1 Critères de blocage d'un déploiement

Un déploiement est bloqué si :

-   les tests de non-régression échouent (cf. L020) ;
-   une migration de schéma n'a pas été validée en recette (cf. L013) ;
-   un secret requis n'est pas disponible dans l'environnement cible.

*Fin de la partie 2/3.*

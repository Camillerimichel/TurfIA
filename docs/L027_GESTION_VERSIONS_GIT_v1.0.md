# L027 --- Gestion des versions Git v1.0

## 1. Objectif

Ce document définit les règles de gestion du dépôt GitHub de TurfIA afin
d'assurer un historique propre, une traçabilité complète et des
livraisons reproductibles.

## 2. Branches

-   **main** : versions stables uniquement.
-   **develop** : branche principale de développement.
-   **feature/***nom* : développements isolés.
-   **hotfix/***nom* : corrections urgentes.

## 3. Commits

Les commits doivent être :

-   atomiques ;
-   documentés ;
-   limités à une seule évolution.

Exemples :

``` text
feat: ajout du moteur TurfIA
fix: correction du calcul ROI
docs: ajout du livrable L031
refactor: simplification du service API
test: ajout des tests statistiques
```

## 4. Versionnement

Le projet suit le schéma :

``` text
MAJEURE.MINEURE.CORRECTIF
```

Exemple :

-   1.0.0
-   1.1.0
-   1.1.1

## 5. Tags

Chaque version publiée reçoit un tag Git :

``` text
v1.0.0
v1.1.0
v2.0.0
```

## 6. Documentation

Toute évolution importante est accompagnée :

-   d'une mise à jour documentaire ;
-   d'un historique Git ;
-   d'une note de version.

## 7. Bonnes pratiques

-   commits fréquents ;
-   messages explicites ;
-   aucune modification directe sur `main` ;
-   suppression des branches fusionnées ;
-   documentation synchronisée avec le code.

## 8. Conclusion

Le dépôt GitHub constitue la référence officielle du projet. Toute
évolution de TurfIA doit être traçable, reproductible et documentée.

# L027 --- Gestion des versions Git v1.0

## 0. Métadonnées du document

| Champ | Valeur |
| --- | --- |
| Identifiant | L027 |
| Niveau documentaire | Spécification technique (cf. L001 §3) |
| Version | 1.0 |
| Documents liés | L014 (arborescence projet), L019 (standards de développement), L028 (gouvernance projet) |

## 1. Objectif

Ce document définit les règles de gestion du dépôt GitHub de TurfIA afin
d'assurer un historique propre, une traçabilité complète et des
livraisons reproductibles. Le dépôt GitHub constitue la référence
unique du projet (cf. L001 §9).

## 2. Branches

-   **main** : versions stables uniquement. Contient uniquement des
    versions validées ; aucun développement direct n'y est réalisé.
-   **develop** : branche principale de développement. Toutes les
    nouvelles fonctionnalités y sont intégrées après validation.
-   **feature/***nom* : développements isolés (ex. `feature/api-statistiques`,
    `feature/dashboard`, `feature/import-pmu`).
-   **hotfix/***nom* : corrections urgentes appliquées directement à
    partir de `main` puis répercutées sur `develop`.

### 2.1 Règle de protection des branches

La branche `main` est protégée : toute intégration s'effectue par
demande de fusion (pull request) revue par au moins une autre personne
que l'auteur (cf. critères de blocage de revue, L019 §10.1), jamais par
un push direct.

## 3. Commits

Chaque commit est atomique, documenté et limité à une seule évolution
fonctionnelle — un commit ne traite qu'une seule évolution afin de
garder un historique facilement compréhensible et de faciliter les
retours en arrière ciblés (`git revert`).

Les messages utilisent la structure suivante :

``` text
type: description
```

Exemples :

``` text
feat: ajout du moteur TurfIA
fix: correction du calcul ROI
docs: ajout du livrable L031
refactor: simplification du service API
test: ajout des tests statistiques
```

## 4. Versionnement

Le projet suit le schéma de versionnement sémantique :

``` text
MAJEURE.MINEURE.CORRECTIF
```

Exemple :

-   1.0.0
-   1.1.0
-   1.1.1

Les versions majeures correspondent à des évolutions incompatibles
(cf. politique de compatibilité ascendante de l'API, L007 §7.1) ; les
versions mineures ajoutent des fonctionnalités rétro-compatibles ; les
correctifs corrigent des anomalies sans changement de comportement
fonctionnel voulu.

## 5. Tags

Chaque version publiée reçoit un tag Git correspondant à une version
livrable :

``` text
v1.0.0
v1.1.0
v2.0.0
```

Un tag n'est créé qu'une fois la version validée en recette (cf. L010
§4.1) ; un tag existant n'est jamais déplacé ni réécrit.

## 6. Documentation

Toute évolution importante est accompagnée :

-   d'une mise à jour documentaire ;
-   d'un historique Git ;
-   d'une note de version précisant nouveautés, corrections, évolutions
    techniques et migrations éventuelles.

## 7. Historique et audit

L'historique Git constitue une source d'information essentielle pour
identifier l'origine d'une évolution, retrouver une version antérieure,
comparer deux états du projet et faciliter les audits (cf. L022).
L'historique n'est jamais réécrit sur les branches partagées (`main`,
`develop`) : `git rebase -i` ou `git push --force` y sont interdits, y
compris pour corriger un message de commit déjà publié.

## 8. Bonnes pratiques

-   commits fréquents ;
-   messages explicites ;
-   aucune modification directe sur `main` (cf. §2.1) ;
-   suppression des branches fusionnées ;
-   documentation synchronisée avec le code.

## 9. Conclusion

Le dépôt GitHub constitue la référence officielle du projet. Toute
évolution de TurfIA doit être traçable, reproductible et documentée.
Cette discipline est ce qui permet à l'ensemble du SAD (cf. L001) de
rester synchronisé avec l'état réel du code au fil du temps.

---

## Historique

| Version | Description |
| --- | --- |
| 1.0 | Version initiale |
| 1.1 | Enrichissement industriel : métadonnées du document, règle de protection de la branche `main`, sémantique du versionnement et des tags, interdiction de réécriture de l'historique partagé. Fusionne le contenu précédemment dupliqué en fin de [L026_GESTION_CONFIGURATION_v1.0.md](L026_GESTION_CONFIGURATION_v1.0.md) |

*Fin du document L027.*

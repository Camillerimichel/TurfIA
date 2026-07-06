# L036_ARCHITECTURE_PERFORMANCES_v2.0

## 0. Métadonnées du document

| Champ | Valeur |
| --- | --- |
| Identifiant | L036 |
| Niveau documentaire | SAD --- Architecture transverse (cf. L001 §3) |
| Version | 2.0 |
| Documents liés | L024 (performances et optimisation, spécification technique), L008/L011/L012 (base SQL) |
| Rôle | Source de référence unique des cibles de performance chiffrées citées dans le reste du corpus (cf. L001 §4.1, L024 §2.1.1) |

## 1. Objet

Ce document décrit l'architecture de gestion des performances de TurfIA.
Il précise les mécanismes permettant de garantir des temps de réponse
compatibles avec les exigences fonctionnelles tout en assurant la montée
en charge.

### 1.1 Cibles de référence

Ces valeurs sont la référence unique citée par les autres documents du
corpus (ex. L001 §4.1, L003 §9.1, L007 §9.1, L024 §2.1.1) :

| Indicateur                              | Cible        |
| ------------------------------------------ | -------------- |
| Temps de réponse API, lecture, p95           | < 300 ms       |
| Temps de réponse API, lecture, p99            | < 800 ms       |
| Durée du batch quotidien complet               | < 1 heure hors incident source de données |
| Disponibilité mensuelle des services            | ≥ 99 %         |

Toute modification de ces cibles est un changement d'architecture
documenté par ADR (cf. §7.1) et répercuté par référence dans les autres
documents, jamais recopié en valeur figée.

## 2. Objectifs

-   Réduire les temps de traitement.
-   Garantir la stabilité des performances.
-   Optimiser les ressources.
-   Mesurer en continu les indicateurs de performance.

## 3. Principes

L'architecture repose sur :

-   optimisation des requêtes SQL ;
-   indexation adaptée ;
-   traitements asynchrones lorsque nécessaire ;
-   limitation des accès redondants ;
-   mise en cache des données stables.

## 4. Indicateurs

Les principaux indicateurs suivis sont :

-   temps moyen de réponse ;
-   temps d'exécution des traitements ;
-   nombre de requêtes ;
-   consommation CPU ;
-   consommation mémoire ;
-   débit des échanges.

## 5. Optimisation

Les traitements sont analysés régulièrement afin d'identifier les
goulots d'étranglement et de prioriser les optimisations.

## 6. Montée en charge

L'architecture permet l'ajout de ressources matérielles ou logiques sans
remise en cause des composants applicatifs.

## 7. Validation

Des campagnes de tests de charge et de performance sont réalisées avant
chaque mise en production majeure.

## 7.1 ADR --- Cibles de performance figées par changement d'architecture

**Contexte** : plusieurs documents citent des cibles de performance ;
sans source unique, ces valeurs divergent inévitablement dans le temps.
**Décision** : les cibles chiffrées de performance sont détenues
exclusivement par ce document (§1.1) et référencées ailleurs.
**Conséquences** : toute évolution de cible passe par une revue
d'architecture (cf. L003 §10), même si elle ne modifie aucun code.

## 8. Conclusion

Cette architecture garantit une plateforme performante, évolutive et
adaptée aux exigences opérationnelles de TurfIA.

---

## Historique

| Version | Description |
| --- | --- |
| 2.0 | Version initiale (Software Architecture Document) |
| 2.1 | Enrichissement industriel : métadonnées du document, cibles de performance de référence (source unique citée par le reste du corpus), ADR de gouvernance de ces cibles |

*Fin du document L036.*

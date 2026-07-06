# L037_ARCHITECTURE_JOURNALISATION_v2.0

## 0. Métadonnées du document

| Champ | Valeur |
| --- | --- |
| Identifiant | L037 |
| Niveau documentaire | SAD --- Architecture transverse (cf. L001 §3) |
| Version | 2.0 |
| Document technique associé | L022 (Journalisation et traçabilité, spécification détaillée) |

## 1. Objet

Ce document décrit l'architecture de journalisation de TurfIA. Il
définit les principes de collecte, de stockage, de conservation et
d'exploitation des journaux applicatifs et techniques.

Le détail des événements journalisés par domaine, le format structuré
recommandé et la liste exhaustive des champs sont spécifiés en L022 ;
ce document se limite aux principes architecturaux transverses.

## 2. Objectifs

-   Assurer la traçabilité des opérations.
-   Faciliter les investigations.
-   Alimenter la supervision.
-   Répondre aux besoins d'audit.

## 3. Types de journaux

Les journaux couvrent :

-   événements applicatifs ;
-   appels API ;
-   traitements planifiés ;
-   accès utilisateurs ;
-   erreurs et exceptions ;
-   opérations d'administration.

## 4. Structure des événements

Chaque événement comprend au minimum :

-   identifiant ;
-   horodatage ;
-   composant ;
-   niveau de sévérité ;
-   contexte ;
-   résultat.

## 5. Centralisation

Les journaux sont consolidés dans un référentiel unique afin de
simplifier les recherches et les corrélations.

## 6. Conservation

Les politiques de rétention distinguent les journaux opérationnels,
techniques et d'audit. Les archives restent accessibles selon les durées
définies par l'exploitation.

Par dérogation à ces durées standard, les journaux fonctionnels
rattachés à une analyse historisée suivent la politique de conservation
immuable définie en L022 §7.1 (alignée sur ADR-002 de L001).

## 7. Exploitation

Les journaux alimentent les tableaux de bord, les alertes, les analyses
de performance et les investigations après incident.

## 8. Conclusion

Cette architecture garantit une journalisation homogène, exploitable et
conforme aux exigences de traçabilité de TurfIA.

---

## Historique

| Version | Description |
| --- | --- |
| 2.0 | Version initiale (Software Architecture Document) |
| 2.1 | Enrichissement industriel : métadonnées du document, renvoi vers L022 pour le détail des événements, dérogation de rétention pour les journaux liés à une analyse historisée |

*Fin du document L037.*

# L038_ARCHITECTURE_SAUVEGARDE_RESTAURATION_v2.0

## 0. Métadonnées du document

| Champ | Valeur |
| --- | --- |
| Identifiant | L038 |
| Niveau documentaire | SAD --- Architecture transverse (cf. L001 §3) |
| Version | 2.0 |
| Documents liés | L011 (schéma SQL), L013 (migrations), L025 (exploitation), L017/L033 (traitements planifiés) |

## 1. Objet

Ce document décrit l'architecture de sauvegarde et de restauration de
TurfIA. Il précise les mécanismes garantissant la protection des données
et la continuité d'exploitation.

## 2. Objectifs

-   Préserver l'intégrité des données.
-   Limiter les pertes en cas d'incident.
-   Réduire le temps de reprise.
-   Garantir la disponibilité des sauvegardes.

## 3. Périmètre

Les sauvegardes couvrent :

-   bases de données ;
-   fichiers de configuration ;
-   journaux ;
-   référentiels ;
-   documents générés.

## 4. Stratégie

Les sauvegardes sont organisées selon plusieurs niveaux :

-   sauvegardes complètes ;
-   sauvegardes incrémentales ;
-   sauvegardes avant déploiement ;
-   archivage longue durée.

### 4.1 Fréquence indicative

| Type de sauvegarde        | Fréquence            |
| --------------------------- | ----------------------- |
| Complète                     | Quotidienne              |
| Incrémentale                  | Selon volumétrie (infra-journalière si nécessaire) |
| Avant déploiement              | À chaque déploiement en production (cf. L010 §7.1) |
| Archivage longue durée          | Mensuelle, conservation étendue |

## 5. Restauration

Les procédures permettent une restauration complète ou partielle en
fonction du périmètre impacté.

## 6. Vérification

Des contrôles réguliers valident la lisibilité des sauvegardes ainsi que
les procédures de restauration.

## 7. Sécurité

Les sauvegardes sont protégées contre les accès non autorisés et
conservées sur des supports distincts de la production.

## 8. Continuité d'activité

Les objectifs de reprise sont définis afin de minimiser l'interruption
des traitements critiques.

### 8.1 Objectifs chiffrés (RPO / RTO)

| Objectif                                   | Cible          |
| --------------------------------------------- | ---------------- |
| RPO (Recovery Point Objective) --- perte de données maximale tolérée | ≤ 24 heures (intervalle entre deux sauvegardes complètes) |
| RTO (Recovery Time Objective) --- délai de restauration maximal toléré | Restauration complète disponible avant l'heure de départ des courses du jour suivant |

Ces objectifs sont réévalués si la fréquence de sauvegarde (§4.1)
évolue ; toute modification est documentée par ADR (cf. §8.2).

### 8.2 ADR --- RPO/RTO alignés sur le cycle quotidien de TurfIA

**Contexte** : TurfIA opère selon un cycle quotidien (cf. L005) ; une
interruption d'un jour est dommageable mais récupérable, contrairement
à une perte de données historisées.
**Décision** : le RPO/RTO ci-dessus est jugé suffisant tant que
l'activité reste organisée autour d'un cycle quotidien unique.
**Conséquences** : une évolution vers un usage temps réel strict (paris
en direct, par exemple) nécessiterait de revoir ces objectifs à la
baisse, ce qui n'est pas dans le périmètre actuel (cf. L002 §2.1
non-objectifs).

## 9. Conclusion

Cette architecture fournit un cadre robuste de sauvegarde et de
restauration adapté aux exigences de disponibilité de TurfIA.

---

## Historique

| Version | Description |
| --- | --- |
| 2.0 | Version initiale (Software Architecture Document) |
| 2.1 | Enrichissement industriel : métadonnées du document, fréquence indicative des sauvegardes, objectifs chiffrés RPO/RTO, ADR de justification de ces objectifs |

*Fin du document L038.*

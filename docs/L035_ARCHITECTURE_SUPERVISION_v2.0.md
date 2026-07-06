# L035_ARCHITECTURE_SUPERVISION_v2.0

## 0. Métadonnées du document

| Champ | Valeur |
| --- | --- |
| Identifiant | L035 |
| Niveau documentaire | SAD --- Architecture transverse (cf. L001 §3) |
| Version | 2.0 |
| Documents liés | L022 (journalisation, spécification technique), L017/L033 (traitements planifiés), L025 (exploitation) |

## 1. Objet

Ce document décrit l'architecture de supervision de TurfIA. Il définit
les mécanismes de surveillance des composants, des traitements et des
flux afin d'assurer la disponibilité et la fiabilité de la plateforme.

Les seuils d'alerte numériques précis pour chaque composant (cf. §6)
sont définis une seule fois, en configuration versionnée (cf. L026), et
référencés depuis les documents techniques concernés (L017 §8.1, L024
§9.1) plutôt que dupliqués ici.

## 2. Objectifs

-   Détection rapide des anomalies.
-   Surveillance continue des services.
-   Suivi des performances.
-   Aide au diagnostic.
-   Production d'indicateurs d'exploitation.

## 3. Composants supervisés

La supervision couvre :

-   API REST ;
-   base de données ;
-   traitements planifiés ;
-   moteurs de calcul ;
-   services externes ;
-   infrastructure système.

## 4. Collecte des métriques

Les métriques portent notamment sur :

-   disponibilité ;
-   temps de réponse ;
-   taux d'erreur ;
-   consommation CPU ;
-   mémoire ;
-   espace disque ;
-   volumes de données traités.

## 5. Journalisation

Les journaux techniques et applicatifs sont centralisés afin de
faciliter les recherches et les audits.

## 6. Alertes

Des seuils configurables déclenchent des alertes en cas de dégradation
des performances, d'échec d'un traitement ou d'indisponibilité d'un
composant.

### 6.1 Niveaux d'alerte et escalade

Les alertes suivent les niveaux de sévérité définis en L021 §14.1
(critique, élevée, modérée) : une alerte critique (ex. base de données
indisponible) déclenche une notification immédiate à l'exploitant
d'astreinte (cf. L025 §4.1), tandis qu'une alerte modérée (ex.
dégradation progressive d'un temps de réponse) est consolidée dans les
tableaux de bord sans notification immédiate.

## 7. Tableaux de bord

Les tableaux de bord présentent les indicateurs d'exploitation, l'état
des traitements, les tendances de performance et l'historique des
incidents.

## 8. Disponibilité

La supervision fonctionne de manière indépendante des traitements métier
afin de rester opérationnelle même lors d'une défaillance partielle du
système.

## 9. Évolutivité

De nouveaux indicateurs peuvent être ajoutés sans modifier
l'architecture générale grâce à une configuration modulaire.

## 10. Conclusion

Cette architecture de supervision assure la visibilité opérationnelle
nécessaire au maintien en conditions opérationnelles de TurfIA.

---

## Historique

| Version | Description |
| --- | --- |
| 2.0 | Version initiale (Software Architecture Document) |
| 2.1 | Enrichissement industriel : métadonnées du document, renvoi vers les seuils versionnés, niveaux d'alerte et procédure d'escalade alignés sur L021/L025 |

*Fin du document L035.*

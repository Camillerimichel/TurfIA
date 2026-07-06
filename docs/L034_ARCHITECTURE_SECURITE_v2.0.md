# L034_ARCHITECTURE_SECURITE_v2.0

## 0. Métadonnées du document

| Champ | Valeur |
| --- | --- |
| Identifiant | L034 |
| Niveau documentaire | SAD --- Architecture transverse (cf. L001 §3) |
| Version | 2.0 |
| Document technique associé | L021 (Sécurité, spécifications détaillées) |
| Référentiel externe | OWASP Top 10, OWASP API Security Top 10 |

## 1. Objet

Ce document décrit l'architecture de sécurité de TurfIA. Il définit les
mécanismes de protection des données, des services et des traitements
conformément aux principes d'une architecture logicielle sécurisée.

Ce document fixe les principes structurants ; les mécanismes détaillés
(politique de mots de passe, format des jetons, contrôles applicatifs
ligne à ligne) sont spécifiés en L021. Les valeurs numériques de
paramétrage (seuils de limitation de débit, durées de session) sont
définies une seule fois, en configuration versionnée (cf. L026), et non
répétées ici pour éviter toute divergence.

## 2. Objectifs

-   Confidentialité des données.
-   Intégrité des traitements.
-   Disponibilité des services.
-   Traçabilité des opérations.
-   Auditabilité des actions.

## 3. Architecture

La sécurité est répartie en plusieurs couches :

1.  Sécurité réseau.
2.  Authentification.
3.  Autorisation.
4.  Protection des données.
5.  Journalisation.
6.  Supervision.

Cette organisation en couches met en œuvre le principe de défense en
profondeur détaillé en L021 §2.2 : la compromission d'une couche ne
doit jamais suffire à compromettre l'ensemble de la plateforme.

### 3.1 ADR --- Aucune exposition directe de la base de données

**Contexte** : la base de données contient l'intégralité des données
métier et historisées.
**Décision** : la base SQL n'est jamais accessible directement depuis
Internet ; tout accès transite par l'API (cf. ADR-004 de L001, L021
§9).
**Conséquences** : simplifie la surface d'attaque à auditer, au prix
d'une dépendance totale à la disponibilité de l'API pour tout accès aux
données.

## 4. Authentification

Les composants techniques utilisent des identités dédiées. Les
utilisateurs sont authentifiés avant tout accès aux fonctionnalités
protégées.

## 5. Gestion des autorisations

Les droits sont attribués selon le principe du moindre privilège et
reposent sur des rôles applicatifs clairement définis.

## 6. Protection des données

Les données sensibles sont chiffrées lors des échanges. Les sauvegardes
suivent les mêmes exigences de protection.

## 7. Journalisation

Toutes les opérations critiques sont enregistrées avec l'identité, la
date, le contexte et le résultat de l'action.

## 8. Résilience

Les mécanismes de sauvegarde, restauration et reprise garantissent la
continuité des traitements après incident.

## 9. Supervision

Les événements de sécurité sont centralisés afin de permettre la
détection rapide des anomalies.

Les niveaux de sévérité d'incident et les délais de réaction attendus
sont ceux définis en L021 §14.1, appliqués uniformément quelle que soit
la couche technique concernée.

## 10. Conclusion

Cette architecture fournit un cadre de sécurité cohérent, évolutif et
compatible avec les exigences opérationnelles de TurfIA.

---

## Historique

| Version | Description |
| --- | --- |
| 2.0 | Version initiale (Software Architecture Document) |
| 2.1 | Enrichissement industriel : métadonnées du document, ADR (aucune exposition directe de la base de données), renvois vers L021 pour les mécanismes détaillés et les niveaux de sévérité d'incident |

*Fin du document L034.*

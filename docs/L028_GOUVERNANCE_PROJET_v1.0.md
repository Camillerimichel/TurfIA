# L028 — Gouvernance du projet

## 0. Métadonnées du document

| Champ | Valeur |
| --- | --- |
| Identifiant | L028 |
| Niveau documentaire | Spécification technique (cf. L001 §3) |
| Version | 1.0 |
| Documents liés | L001 (gouvernance documentaire), L003 (RACI d'architecture), L027 (gestion des versions Git) |

## 1. Objectif

### 1.1 Finalité

La gouvernance du projet définit l'organisation générale de TurfIA, les responsabilités des différents composants et les règles de décision applicables à l'évolution du projet.

Elle garantit :

- la stabilité du modèle ;
- la traçabilité des décisions ;
- la reproductibilité des analyses ;
- la cohérence des évolutions.

---

## 2. Principes

### 2.1 Référentiel unique

Le dépôt GitHub constitue la référence officielle du projet.

Aucun développement ne doit être réalisé en dehors de ce référentiel.

---

### 2.2 Documentation

Toute évolution importante est accompagnée :

- d'une mise à jour documentaire ;
- d'une migration éventuelle ;
- de tests ;
- d'une traçabilité Git.

Le code et la documentation évoluent simultanément.

### 2.3 Rôles de gouvernance

| Rôle                  | Responsabilité principale                              |
| ----------------------- | ---------------------------------------------------------- |
| Propriétaire du SAD       | Approbation des évolutions architecturales majeures (cf. L001 §9.1) |
| Architecte logiciel       | Analyse d'impact, cohérence documentaire (cf. L003 §10.1)  |
| Développeur                | Implémentation, revue de code (cf. L019 §10)               |
| Exploitant                  | Validation opérationnelle, suivi post-déploiement (cf. L025) |

---

## 3. Gouvernance fonctionnelle

### 3.1 Objectifs

Les décisions fonctionnelles concernent notamment :

- les règles TurfIA ;
- les pondérations ;
- les statistiques ;
- les propositions de paris ;
- les tableaux de bord.

---

### 3.2 Validation

Toute évolution fonctionnelle doit être validée :

- par des résultats historiques ;
- par une amélioration mesurable ;
- par une absence de régression.

---

## 4. Gouvernance technique

Les évolutions techniques concernent notamment :

- architecture ;
- API ;
- SQL ;
- performances ;
- sécurité ;
- automatisations.

Elles doivent rester compatibles avec les objectifs fonctionnels.

---

## 5. Cycle d'évolution

Toute évolution suit le cycle suivant :

```text
Analyse

      │

      ▼

Documentation

      │

      ▼

Développement

      │

      ▼

Tests

      │

      ▼

Validation

      │

      ▼

Déploiement

      │

      ▼

Suivi
```

---

## 6. Gestion des versions

Chaque évolution est associée :

- à un numéro de version ;
- à un commit Git ;
- à une documentation ;
- à une date de publication.

---

## 7. Indicateurs

Les principaux indicateurs de gouvernance sont :

- nombre d'évolutions ;
- taux de réussite des tests ;
- couverture documentaire ;
- couverture des tests ;
- évolution du ROI ;
- stabilité du modèle.

---

## 8. Gestion des anomalies

Chaque anomalie est :

- identifiée ;
- documentée ;
- corrigée ;
- testée ;
- historisée.

Une anomalie corrigée ne doit pas réapparaître.

---

## 9. Amélioration continue

Toute amélioration du modèle TurfIA est validée uniquement après comparaison avec les résultats historiques.

Aucune modification n'est effectuée sur la base d'une intuition ou d'un cas isolé.

---

## 10. Conclusion

La gouvernance garantit la stabilité, la qualité et la pérennité de TurfIA en assurant une évolution maîtrisée de l'ensemble du projet.

---

## Historique

| Version | Description |
| --- | --- |
| 1.0 | Version initiale |
| 1.1 | Enrichissement industriel : métadonnées du document, rôles de gouvernance. Correction de structure : le glossaire précédemment dupliqué en fin de ce fichier sous un en-tête « L029 » a été fusionné dans le document dédié [L029_GLOSSAIRE_v1.0.md](L029_GLOSSAIRE_v1.0.md) auquel il appartient, sans perte d'information |

*Fin du document L028.*
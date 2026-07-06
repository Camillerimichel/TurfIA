# L028 — Gouvernance du projet

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

# L029 — Glossaire

## 1. Objectif

Le présent glossaire définit les principaux termes utilisés dans la documentation officielle de TurfIA.

Les définitions s'appliquent à l'ensemble du projet.

---

## 2. Définitions

| Terme          | Définition                                                   |
| -------------- | ------------------------------------------------------------ |
| Analyse        | Calcul réalisé par TurfIA sur une course                     |
| Analyse finale | Analyse recalculée avant le départ officiel                  |
| API            | Interface de programmation de TurfIA                         |
| Base           | Cheval présentant la meilleure probabilité de réussite       |
| Cote           | Valeur fournie par un opérateur de paris                     |
| Discipline     | Plat, Trot, Obstacle…                                        |
| Historique     | Ensemble des analyses conservées                             |
| Hippodrome     | Lieu où se déroule une réunion                               |
| Outsider       | Cheval peu joué mais jugé compétitif                         |
| Pari           | Recommandation produite par TurfIA                           |
| Partant        | Cheval officiellement déclaré au départ                      |
| Pré-analyse    | Première analyse réalisée avant la course                    |
| Quinté+        | Course support principale analysée par TurfIA                |
| Réunion        | Ensemble des courses d'un même hippodrome                    |
| ROI            | Retour sur investissement                                    |
| Score TurfIA   | Indicateur synthétique de confiance                          |
| Sélection      | Liste des chevaux retenus                                    |
| Tocard         | Cheval spéculatif à forte cote                               |
| Value Bet      | Cheval dont la probabilité estimée est supérieure à celle implicite de la cote |

---

## 3. Abréviations

| Abréviation | Signification                                  |
| ----------- | ---------------------------------------------- |
| API         | Application Programming Interface              |
| CI/CD       | Continuous Integration / Continuous Deployment |
| CRUD        | Create Read Update Delete                      |
| JSON        | JavaScript Object Notation                     |
| REST        | Representational State Transfer                |
| ROI         | Return On Investment                           |
| SQL         | Structured Query Language                      |
| TLS         | Transport Layer Security                       |
| VPS         | Virtual Private Server                         |

---

## 4. Conclusion

Le glossaire constitue la terminologie officielle utilisée dans l'ensemble de la documentation TurfIA.
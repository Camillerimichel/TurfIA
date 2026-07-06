# L012 — Vues SQL

## 0. Métadonnées du document

| Champ | Valeur |
| --- | --- |
| Identifiant | L012 |
| Niveau documentaire | Spécification technique (cf. L001 §3) |
| Version | 1.0 |
| Dépend de | L011 (Schéma SQL) |
| Consommé par | L007/L032.x (API), L018 (Interface HTML), L024/L036 (Performances) |

## 1. Objectif

### 1.1 Finalité

Les vues SQL constituent la couche de lecture de TurfIA.

Elles ont pour objectif de :

- simplifier les requêtes ;
- factoriser les traitements ;
- normaliser les calculs ;
- accélérer le développement de l'API ;
- fournir une base commune aux tableaux de bord.

Aucune vue ne contient de logique métier complexe.

---

### 1.2 Principes

Les vues respectent les règles suivantes :

- lecture uniquement ;
- aucune modification de données ;
- calculs déterministes ;
- nommage homogène ;
- documentation obligatoire.

---

### 1.3 Organisation

Les vues sont réparties selon les familles suivantes :

```
vw_reference_*

vw_course_*

vw_partant_*

vw_analyse_*

vw_statistique_*

vw_reporting_*
```

---

## 2. Architecture des vues

### 2.1 Principe

Les vues constituent une couche intermédiaire.

```
Tables SQL

        │

        ▼

     Vues SQL

        │

        ▼

 API REST

        │

        ▼

 Interface HTML
```

---

### 2.2 Avantages

Cette architecture permet :

- moins de SQL dans l'API ;
- maintenance simplifiée ;
- homogénéité des calculs ;
- optimisation des performances.

### 2.3 Sécurité et droits d'accès

Les vues sont le point d'accès privilégié du rôle applicatif
`turfia_readonly` (cf. L011 §16.5) : ce rôle dispose de droits `SELECT`
sur les vues mais d'aucun droit direct sur les tables sous-jacentes,
ce qui garantit qu'aucun consommateur en lecture ne dépend d'un détail
d'implémentation du schéma physique.

### 2.4 Contrat de stabilité

Une vue constitue un contrat vis-à-vis de ses consommateurs (API,
rapports) : la suppression ou le renommage d'une colonne exposée par une
vue est traité comme un changement cassant, soumis à la même politique
de compatibilité ascendante que l'API elle-même (cf. L007 §7.1).

---

## 3. Vues de référence

### 3.1 Objectif

Ces vues regroupent les informations provenant des tables de référence.

---

### 3.2 vw_reference_hippodrome

Contient notamment :

- nom
- ville
- pays
- corde
- surface principale

---

### 3.3 vw_reference_discipline

Liste des disciplines.

---

### 3.4 vw_reference_distance

Distances disponibles.

---

### 3.5 vw_reference_course

Types de courses.

---

## 4. Vues métier

### 4.1 vw_course

Vue principale des courses.

Colonnes principales :

- date
- hippodrome
- réunion
- course
- discipline
- distance
- allocation
- nombre de partants

---

### 4.2 vw_partant

Vue complète des partants.

Elle regroupe notamment :

- cheval
- jockey
- entraîneur
- numéro
- corde
- poids
- musique
- valeur
- gains

---

### 4.3 vw_cote

Historique des cotes.

Colonnes :

- opérateur
- cote
- date
- évolution

---

### 4.4 vw_resultat

Résultats officiels.

Elle présente :

- classement
- temps
- écarts
- rapports éventuels

---

## 5. Vues d'analyse

### 5.1 Objectif

Ces vues exposent les résultats calculés par TurfIA.

---

### 5.2 vw_analyse

Informations générales.

Colonnes :

- score
- risque
- ROI théorique
- décision

---

### 5.3 vw_classement

Classement TurfIA.

Colonnes :

- rang
- cheval
- score
- consensus
- value bet

---

### 5.4 vw_selection

Synthèse :

- bases
- chances régulières
- outsiders
- tocard

---

### 5.5 vw_paris

Liste des paris recommandés.

---

## 6. Vues statistiques

### 6.1 vw_roi_global

Affiche :

- nombre de courses
- gains
- pertes
- ROI

---

### 6.2 vw_roi_score

ROI par tranche de confiance.

Exemple :

| Score | ROI  |
| ----- | ---- |
| <60   | ...  |
| 60-74 | ...  |
| 75-84 | ...  |
| ≥85   | ...  |

---

### 6.3 vw_roi_hippodrome

ROI par hippodrome.

---

### 6.4 vw_roi_discipline

ROI par discipline.

---

### 6.5 vw_roi_pari

ROI par type de pari.

---

## 7. Vues Reporting

### 7.1 Objectif

Ces vues alimentent directement les tableaux de bord.

---

### 7.2 vw_dashboard_jour

Courses du jour.

---

### 7.3 vw_dashboard_roi

Évolution du ROI.

---

### 7.4 vw_dashboard_model

Performances du modèle.

---

### 7.5 vw_dashboard_historique

Historique des analyses.

---

## 8. Conventions de nommage

Toutes les vues utilisent le préfixe :

```
vw_
```

Exemples :

```
vw_course

vw_partant

vw_analyse

vw_roi_global
```

---

## 9. Optimisation

Les vues doivent :

- utiliser les index existants ;
- éviter les sous-requêtes inutiles ;
- limiter les jointures ;
- privilégier les calculs simples.

Les vues les plus coûteuses pourront être matérialisées ultérieurement.

### 9.1 Critères de matérialisation

Une vue est candidate à la matérialisation (`MATERIALIZED VIEW`)
uniquement si les trois conditions suivantes sont réunies : elle est
consultée fréquemment, son calcul sous-jacent est coûteux (mesuré, cf.
L024/L036), et une latence de rafraîchissement (ex. horaire ou
quotidienne) est fonctionnellement acceptable — ce qui exclut par
construction les vues utilisées en décision temps réel (ex.
`vw_cote`).

---

## 10. Évolutivité

Les vues constituent l'interface SQL officielle de TurfIA.

L'API, les rapports HTML et les outils statistiques doivent privilégier ces vues plutôt que les tables brutes.

Cette organisation permet de faire évoluer le modèle relationnel sans remettre en cause les couches supérieures de l'application.

---

## Historique

| Version | Description |
| --- | --- |
| 1.0 | Version initiale |
| 1.1 | Enrichissement industriel : métadonnées du document, sécurité et droits d'accès par rôle, contrat de stabilité des vues, critères de matérialisation |

*Fin du document L012.*
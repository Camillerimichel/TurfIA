# TurfIA

## L008_BASE_SQL_v1.0

**Version :** 1.0  
**Statut :** Validé  
**Objet :** Spécification de la base SQL TurfIA

---

## Objectif

Ce livrable décrit la base SQL de TurfIA. La base doit permettre de stocker les données de courses, les partants, les cotes, les analyses, les paris proposés, les résultats officiels, les historiques, les statistiques et les tâches planifiées.

La base SQL est la source de vérité opérationnelle du projet. Elle doit garantir l'historisation, la traçabilité et la reproductibilité des analyses.

---

## Principes de conception

La base TurfIA respecte les principes suivants :

- données normalisées ;
- clés techniques immuables ;
- historisation complète ;
- absence de suppression logique des analyses validées ;
- intégrité référentielle ;
- horodatage systématique ;
- séparation entre données sources, analyses et résultats ;
- compatibilité avec SQLite en développement et PostgreSQL en cible possible.

---

## Conventions de nommage

Les noms de tables et colonnes utilisent :

- minuscules ;
- séparateur `_` ;
- noms explicites ;
- clés primaires au format `table_id` ;
- clés étrangères au format `table_id` de la table référencée.

Exemple :

```text
course_id
partant_id
analyse_id
```

---

## Tables principales

Le modèle initial comprend les tables suivantes :

- `courses` ;
- `partants` ;
- `cotes` ;
- `consensus_presse` ;
- `analyses` ;
- `classements_analyse` ;
- `paris` ;
- `resultats` ;
- `rapports_pmu` ;
- `historiques` ;
- `statistiques` ;
- `taches_planifiees` ;
- `logs_execution` ;
- `versions_modele`.

---

## Table `courses`

### Objet

Stocker les informations générales d'une course.

### Colonnes principales

| Colonne | Type indicatif | Description |
|---------|----------------|-------------|
| course_id | INTEGER PK | Identifiant technique |
| date_course | DATE | Date de la course |
| hippodrome | TEXT | Hippodrome |
| nom_course | TEXT | Nom de la course |
| numero_course | INTEGER | Numéro de course |
| heure_depart | TIME | Heure officielle |
| discipline | TEXT | Plat, trot, obstacle, etc. |
| distance_m | INTEGER | Distance en mètres |
| corde | TEXT | Corde ou sens de parcours |
| surface | TEXT | Herbe, sable, PSF, etc. |
| etat_terrain | TEXT | État du terrain ou de la piste |
| allocation | REAL | Allocation |
| conditions_course | TEXT | Conditions textuelles |
| nb_partants_annonce | INTEGER | Nombre initial de partants |
| statut | TEXT | prévue, analysée, courue, contrôlée |
| created_at | DATETIME | Création |
| updated_at | DATETIME | Mise à jour |

### Contraintes

- `date_course`, `hippodrome`, `numero_course` doivent permettre d'identifier une course.
- Une course contrôlée ne doit pas être supprimée.

---

## Table `partants`

### Objet

Stocker les chevaux engagés dans une course.

### Colonnes principales

| Colonne | Type indicatif | Description |
|---------|----------------|-------------|
| partant_id | INTEGER PK | Identifiant technique |
| course_id | INTEGER FK | Course liée |
| numero | INTEGER | Numéro du cheval |
| nom_cheval | TEXT | Nom du cheval |
| entraineur | TEXT | Entraîneur |
| jockey_driver | TEXT | Jockey ou driver |
| musique | TEXT | Performances récentes |
| valeur_handicap | REAL | Valeur handicap si disponible |
| age | INTEGER | Âge |
| sexe | TEXT | Sexe |
| poids | REAL | Poids porté si applicable |
| statut | TEXT | partant, non_partant |
| created_at | DATETIME | Création |
| updated_at | DATETIME | Mise à jour |

### Contraintes

- unicité de `(course_id, numero)` ;
- un non-partant doit rester historisé.

---

## Table `cotes`

### Objet

Historiser les cotes observées.

### Colonnes principales

| Colonne | Type indicatif | Description |
|---------|----------------|-------------|
| cote_id | INTEGER PK | Identifiant technique |
| course_id | INTEGER FK | Course |
| partant_id | INTEGER FK | Partant |
| source | TEXT | PMU ou autre source |
| cote | REAL | Cote observée |
| horodatage | DATETIME | Moment de l'observation |
| type_cote | TEXT | gagnant, placé, autre |
| created_at | DATETIME | Création |

### Contraintes

- les cotes ne sont jamais écrasées ;
- chaque nouvelle observation crée une nouvelle ligne.

---

## Table `consensus_presse`

### Objet

Stocker les indicateurs de consensus presse par partant.

### Colonnes principales

| Colonne | Type indicatif | Description |
|---------|----------------|-------------|
| consensus_id | INTEGER PK | Identifiant technique |
| course_id | INTEGER FK | Course |
| partant_id | INTEGER FK | Partant |
| source | TEXT | Source presse ou agrégateur |
| nb_citations | INTEGER | Nombre de citations |
| pourcentage_citations | REAL | Pourcentage de citations |
| rang_consensus | INTEGER | Rang presse |
| horodatage | DATETIME | Moment de l'observation |
| created_at | DATETIME | Création |

---

## Table `versions_modele`

### Objet

Identifier les versions du modèle TurfIA utilisées dans les analyses.

### Colonnes principales

| Colonne | Type indicatif | Description |
|---------|----------------|-------------|
| version_modele_id | INTEGER PK | Identifiant technique |
| nom_version | TEXT | Nom de version |
| date_activation | DATE | Date d'entrée en vigueur |
| description | TEXT | Description des règles |
| statut | TEXT | brouillon, active, archivée |
| created_at | DATETIME | Création |

---

## Table `analyses`

### Objet

Stocker les pré-analyses et analyses finales.

### Colonnes principales

| Colonne | Type indicatif | Description |
|---------|----------------|-------------|
| analyse_id | INTEGER PK | Identifiant technique |
| course_id | INTEGER FK | Course analysée |
| version_modele_id | INTEGER FK | Version du modèle |
| type_analyse | TEXT | preanalyse ou finale |
| analyse_parent_id | INTEGER FK nullable | Analyse précédente liée |
| score_confiance | INTEGER | Score 0 à 100 |
| niveau_risque | TEXT | faible, moyen, élevé |
| roi_theorique | REAL | ROI estimé |
| decision | TEXT | ne_pas_jouer, jouer_prudemment, jouer_normalement, opportunite_forte |
| budget_recommande | REAL | Budget recommandé |
| synthese | TEXT | Synthèse argumentée |
| statut | TEXT | brouillon, validée, incomplète |
| donnees_manquantes | TEXT | Données absentes ou incertaines |
| created_at | DATETIME | Création |
| updated_at | DATETIME | Mise à jour |

### Contraintes

- une analyse validée ne doit pas être modifiée ;
- une correction crée une nouvelle analyse liée par `analyse_parent_id`.

---

## Table `classements_analyse`

### Objet

Stocker le classement des partants pour une analyse donnée.

### Colonnes principales

| Colonne | Type indicatif | Description |
|---------|----------------|-------------|
| classement_id | INTEGER PK | Identifiant technique |
| analyse_id | INTEGER FK | Analyse |
| partant_id | INTEGER FK | Partant |
| rang_turfia | INTEGER | Rang TurfIA |
| score_partant | REAL | Score individuel |
| categorie | TEXT | base, chance_reguliere, outsider, tocard |
| justification | TEXT | Argument synthétique |
| created_at | DATETIME | Création |

---

## Table `paris`

### Objet

Stocker les paris proposés par TurfIA.

### Colonnes principales

| Colonne | Type indicatif | Description |
|---------|----------------|-------------|
| pari_id | INTEGER PK | Identifiant technique |
| analyse_id | INTEGER FK | Analyse liée |
| type_pari | TEXT | Simple Gagnant, Simple Placé, Couplé, etc. |
| selection | TEXT | Sélection proposée |
| mise | REAL | Mise recommandée |
| justification | TEXT | Justification |
| gain | REAL | Gain constaté après résultat |
| resultat | TEXT | gagné, perdu, remboursé, non_joué |
| created_at | DATETIME | Création |
| updated_at | DATETIME | Mise à jour |

---

## Table `resultats`

### Objet

Stocker l'arrivée officielle d'une course.

### Colonnes principales

| Colonne | Type indicatif | Description |
|---------|----------------|-------------|
| resultat_id | INTEGER PK | Identifiant technique |
| course_id | INTEGER FK | Course |
| arrivee_officielle | TEXT | Ordre officiel |
| non_partants | TEXT | Non-partants confirmés |
| source | TEXT | Source officielle |
| horodatage | DATETIME | Moment de récupération |
| created_at | DATETIME | Création |

---

## Table `rapports_pmu`

### Objet

Stocker les rapports officiels permettant de calculer les gains.

### Colonnes principales

| Colonne | Type indicatif | Description |
|---------|----------------|-------------|
| rapport_id | INTEGER PK | Identifiant technique |
| resultat_id | INTEGER FK | Résultat lié |
| type_pari | TEXT | Type de pari |
| combinaison | TEXT | Combinaison gagnante |
| rapport_pour_un_euro | REAL | Rapport unitaire |
| created_at | DATETIME | Création |

---

## Table `historiques`

### Objet

Stocker le bilan financier et décisionnel de chaque course contrôlée.

### Colonnes principales

| Colonne | Type indicatif | Description |
|---------|----------------|-------------|
| historique_id | INTEGER PK | Identifiant technique |
| course_id | INTEGER FK | Course |
| analyse_id | INTEGER FK | Analyse finale |
| resultat_id | INTEGER FK | Résultat |
| date_operation | DATE | Date du contrôle |
| score_confiance | INTEGER | Score final |
| decision | TEXT | Décision finale |
| mise | REAL | Mise totale |
| gains | REAL | Gains totaux |
| profit | REAL | Gains moins mise |
| roi | REAL | ROI course |
| commentaire | TEXT | Analyse critique |
| created_at | DATETIME | Création |

---

## Table `statistiques`

### Objet

Stocker les agrégats de performance.

### Colonnes principales

| Colonne | Type indicatif | Description |
|---------|----------------|-------------|
| statistique_id | INTEGER PK | Identifiant technique |
| periode | TEXT | Période de calcul |
| date_calcul | DATE | Date de calcul |
| nb_courses | INTEGER | Courses analysées |
| nb_jouees | INTEGER | Courses jouées |
| nb_evitees | INTEGER | Courses évitées |
| taux_reussite | REAL | Taux de réussite |
| mises_cumulees | REAL | Total mises |
| gains_cumules | REAL | Total gains |
| pertes_cumulees | REAL | Total pertes |
| profit_cumule | REAL | Profit cumulé |
| roi_global | REAL | ROI global |
| roi_par_confiance | TEXT | Agrégat JSON ou texte structuré |
| roi_par_type_pari | TEXT | Agrégat JSON ou texte structuré |
| created_at | DATETIME | Création |

---

## Table `taches_planifiees`

### Objet

Stocker les tâches d'automatisation.

### Colonnes principales

| Colonne | Type indicatif | Description |
|---------|----------------|-------------|
| tache_id | INTEGER PK | Identifiant technique |
| procedure | TEXT | preanalyse, analyse_finale, controle_resultat |
| frequence | TEXT | quotidienne, relative_depart, manuelle |
| derniere_execution | DATETIME | Dernière exécution |
| prochaine_execution | DATETIME | Prochaine exécution |
| statut | TEXT | active, inactive, erreur |
| created_at | DATETIME | Création |
| updated_at | DATETIME | Mise à jour |

---

## Table `logs_execution`

### Objet

Tracer les traitements exécutés.

### Colonnes principales

| Colonne | Type indicatif | Description |
|---------|----------------|-------------|
| log_id | INTEGER PK | Identifiant technique |
| tache_id | INTEGER FK nullable | Tâche liée |
| procedure | TEXT | Procédure exécutée |
| niveau | TEXT | info, warning, error |
| message | TEXT | Message |
| ressource_type | TEXT | Type de ressource affectée |
| ressource_id | INTEGER | Identifiant de ressource |
| horodatage | DATETIME | Horodatage |

---

## Index recommandés

Index minimaux :

- `courses(date_course)` ;
- `courses(hippodrome)` ;
- `partants(course_id)` ;
- `cotes(course_id, partant_id, horodatage)` ;
- `consensus_presse(course_id, partant_id)` ;
- `analyses(course_id, type_analyse)` ;
- `analyses(score_confiance)` ;
- `classements_analyse(analyse_id)` ;
- `paris(analyse_id)` ;
- `resultats(course_id)` ;
- `historiques(date_operation)` ;
- `historiques(score_confiance)` ;
- `logs_execution(horodatage)`.

---

## Règles d'intégrité

Les règles minimales sont :

- un partant appartient toujours à une course ;
- une cote appartient toujours à un partant et une course ;
- une analyse appartient toujours à une course ;
- un classement appartient toujours à une analyse ;
- un pari appartient toujours à une analyse ;
- un résultat appartient toujours à une course ;
- un historique appartient toujours à une analyse finale et à un résultat ;
- les analyses validées sont immuables fonctionnellement.

---

## Données structurées dans des colonnes texte

Certaines colonnes peuvent contenir temporairement du texte structuré ou du JSON :

- `selection` ;
- `arrivee_officielle` ;
- `non_partants` ;
- `roi_par_confiance` ;
- `roi_par_type_pari` ;
- `donnees_manquantes`.

Cette solution est acceptable en version initiale. Les structures très utilisées pourront être normalisées dans des tables dédiées lors d'une version ultérieure.

---

## Sauvegarde et historique

La base doit être sauvegardée régulièrement.

Les tables critiques sont :

- `analyses` ;
- `classements_analyse` ;
- `paris` ;
- `resultats` ;
- `historiques` ;
- `statistiques`.

Les résultats historiques ne doivent jamais être réécrits pour améliorer artificiellement les performances passées.

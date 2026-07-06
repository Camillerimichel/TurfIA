# L019 — Standards de développement

## 1. Objectif

### 1.1 Finalité

Ce document définit les règles de développement applicables à l'ensemble du projet TurfIA.

Son objectif est de garantir :

- un code homogène ;
- une maintenance facilitée ;
- une qualité constante ;
- une évolution maîtrisée ;
- une réduction des risques de régression.

Ces règles s'appliquent à tous les composants du projet.

---

## 2. Principes généraux

### 2.1 Lisibilité

Le code doit être :

- simple ;
- lisible ;
- documenté ;
- facilement compréhensible plusieurs années après son écriture.

La simplicité est privilégiée à l'optimisation prématurée.

---

### 2.2 Responsabilité unique

Chaque élément possède une seule responsabilité.

Cela concerne notamment :

- les classes ;
- les fonctions ;
- les modules ;
- les services.

Une fonction ne réalise qu'un seul traitement.

---

### 2.3 Modularité

Le projet est composé de modules indépendants.

Les dépendances entre modules doivent rester limitées.

Les dépendances circulaires sont interdites.

---

## 3. Conventions de nommage

### 3.1 Fichiers

Les fichiers utilisent exclusivement :

- minuscules ;
- caractères ASCII ;
- caractère "_".

Exemples :

```text
analyse_service.py
course_repository.py
calcul_score.py
```

---

### 3.2 Classes

Les classes utilisent le format PascalCase.

Exemples :

```text
AnalyseService

CourseRepository

ScoreCalculator

ImportManager
```

---

### 3.3 Fonctions

Les fonctions utilisent le format snake_case.

Exemples :

```text
calculer_score()

charger_courses()

generer_selection()
```

---

### 3.4 Variables

Les noms de variables doivent être explicites.

Exemples :

```text
score_confiance

liste_partants

date_course

roi_global
```

Les abréviations sont évitées lorsqu'elles nuisent à la compréhension.

---

## 4. Organisation des fichiers

Chaque fichier contient :

- une seule responsabilité principale ;
- les imports ;
- les constantes ;
- les classes ;
- les fonctions publiques ;
- les fonctions privées.

La longueur d'un fichier doit rester raisonnable.

---

## 5. Fonctions

### 5.1 Taille

Les fonctions doivent rester courtes.

Lorsqu'une fonction devient difficile à lire, elle est découpée.

---

### 5.2 Paramètres

Le nombre de paramètres doit rester limité.

Lorsque plusieurs paramètres sont liés, ils sont regroupés dans un objet métier.

---

### 5.3 Valeurs de retour

Une fonction possède une valeur de retour clairement définie.

Les effets de bord doivent être limités.

---

## 6. Gestion des erreurs

Les erreurs sont systématiquement :

- interceptées ;
- journalisées ;
- propagées lorsque nécessaire.

Les exceptions ne doivent jamais être ignorées.

---

## 7. Journalisation

Les journaux doivent permettre :

- de comprendre un incident ;
- de reproduire un problème ;
- de suivre les traitements.

Les informations confidentielles ne sont jamais enregistrées.

---

## 8. Documentation

Chaque module comporte :

- un objectif ;
- une description ;
- les principales responsabilités.

Les fonctions publiques sont documentées.

Les algorithmes complexes comportent une explication de leur logique.

---

## 9. Tests

Chaque nouveau développement est accompagné de tests adaptés.

Les catégories de tests comprennent :

- tests unitaires ;
- tests d'intégration ;
- tests fonctionnels ;
- tests de performance lorsque nécessaire.

Une correction d'anomalie est accompagnée d'un test reproduisant le problème corrigé.

---

## 10. Revue de code

Avant toute intégration, une revue vérifie notamment :

- lisibilité ;
- respect des conventions ;
- couverture des tests ;
- impact sur les performances ;
- sécurité ;
- documentation.

---

## 11. Performances

Les optimisations sont réalisées uniquement lorsqu'un besoin est identifié.

Les performances sont mesurées avant toute modification importante.

Une optimisation ne doit jamais rendre le code difficile à maintenir.

---

## 12. Sécurité

Les principes suivants sont appliqués :

- validation des entrées ;
- contrôle des autorisations ;
- protection des secrets ;
- limitation des privilèges ;
- journalisation des actions sensibles.

La sécurité est prise en compte dès la conception.

---

## 13. Gestion des dépendances

Toute nouvelle dépendance doit être justifiée.

Les critères d'évaluation comprennent notamment :

- stabilité ;
- maintenance ;
- licence ;
- communauté ;
- pérennité.

Les dépendances inutilisées sont supprimées régulièrement.

---

## 14. Évolutivité

Le code est conçu pour :

- accueillir de nouveaux algorithmes ;
- intégrer de nouvelles sources de données ;
- ajouter de nouveaux indicateurs ;
- supporter de nouvelles interfaces.

Les évolutions ne doivent pas remettre en cause les composants existants.

---

## 15. Conclusion

Ces standards constituent le référentiel de développement de TurfIA.

Ils garantissent une base logicielle homogène, robuste, maintenable et évolutive, adaptée à un projet destiné à évoluer sur plusieurs années.
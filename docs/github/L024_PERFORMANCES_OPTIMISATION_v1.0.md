# L024 — Performance et optimisation

## 1. Objectif

### 1.1 Finalité

La politique de performance de TurfIA définit les règles permettant de maintenir un niveau élevé de réactivité tout en garantissant la fiabilité des traitements.

Les objectifs sont :

- réduire les temps de réponse ;
- optimiser les traitements quotidiens ;
- maîtriser la consommation des ressources ;
- assurer la montée en charge ;
- préserver la maintenabilité du code.

L'optimisation ne doit jamais compromettre la lisibilité de l'application.

---

## 2. Principes

### 2.1 Mesurer avant d'optimiser

Toute optimisation doit être précédée d'une mesure objective.

Les décisions sont fondées sur :

- les temps d'exécution ;
- les statistiques système ;
- les journaux applicatifs ;
- les indicateurs de supervision.

Aucune optimisation ne doit être réalisée sur une simple intuition.

---

### 2.2 Priorités

Les optimisations concernent en priorité :

- les traitements quotidiens ;
- les analyses TurfIA ;
- les calculs statistiques ;
- les accès à la base SQL ;
- les tableaux de bord.

---

## 3. Performances applicatives

### 3.1 Temps de réponse

Les temps de réponse doivent rester compatibles avec une utilisation interactive.

Les traitements longs sont exécutés de manière asynchrone.

---

### 3.2 Réduction des appels

Les échanges entre les différentes couches applicatives sont limités au strict nécessaire.

Les traitements redondants sont supprimés.

---

### 3.3 Mutualisation

Les calculs identiques sont réalisés une seule fois puis réutilisés.

Cette règle concerne notamment :

- les statistiques ;
- les agrégations ;
- les calculs de scores intermédiaires.

---

## 4. Optimisation SQL

### 4.1 Requêtes

Les requêtes SQL doivent :

- utiliser les index disponibles ;
- limiter les jointures inutiles ;
- éviter les sous-requêtes coûteuses ;
- sélectionner uniquement les colonnes nécessaires.

---

### 4.2 Index

Les index sont créés uniquement lorsqu'ils apportent un gain significatif.

Ils sont régulièrement analysés afin de supprimer ceux devenus inutiles.

---

### 4.3 Vues

Les vues SQL simplifient les traitements de lecture.

Les vues les plus sollicitées pourront être matérialisées lorsque les volumes le justifieront.

---

## 5. Optimisation mémoire

### 5.1 Chargement des données

Les données sont chargées uniquement lorsqu'elles sont nécessaires.

Les traitements utilisent la pagination ou le traitement par lots lorsque les volumes deviennent importants.

---

### 5.2 Objets temporaires

Les objets temporaires sont libérés dès qu'ils ne sont plus utilisés.

La consommation mémoire est surveillée en permanence.

---

## 6. Optimisation des traitements

### 6.1 Traitements quotidiens

Les analyses quotidiennes sont exécutées dans l'ordre suivant :

1. import des données ;
2. pré-analyse ;
3. analyse finale ;
4. contrôle des résultats ;
5. calcul des statistiques.

Cette organisation limite les recalculs inutiles.

---

### 6.2 Traitements parallèles

Lorsque cela est pertinent, certains traitements peuvent être parallélisés.

Les traitements indépendants sont privilégiés afin de limiter les risques de contention.

---

## 7. Interface utilisateur

### 7.1 Chargement

Les pages chargent uniquement les informations nécessaires à leur affichage.

Les listes importantes utilisent :

- pagination ;
- filtrage ;
- tri.

---

### 7.2 Ressources statiques

Les ressources statiques bénéficient :

- d'une mise en cache ;
- d'une compression ;
- d'une optimisation des formats.

---

## 8. API REST

### 8.1 Optimisation

L'API applique notamment :

- pagination ;
- limitation des résultats ;
- validation rapide des requêtes ;
- sérialisation optimisée.

---

### 8.2 Traitements longs

Les traitements nécessitant plusieurs secondes sont délégués aux automatisations.

L'API reste disponible pour les autres utilisateurs.

---

## 9. Supervision

### 9.1 Indicateurs

Les principaux indicateurs suivis sont :

- temps moyen de réponse ;
- temps maximal ;
- nombre de requêtes ;
- utilisation CPU ;
- mémoire ;
- activité disque ;
- activité réseau.

---

### 9.2 Analyse

Les indicateurs permettent :

- d'identifier les ralentissements ;
- d'anticiper les saturations ;
- de planifier les évolutions.

---

## 10. Évolutivité

### 10.1 Montée en charge

L'architecture doit permettre :

- l'augmentation du nombre de courses analysées ;
- l'ajout de nouvelles statistiques ;
- l'intégration de nouvelles sources de données ;
- l'augmentation du nombre d'utilisateurs.

---

### 10.2 Optimisations futures

Les évolutions pourront notamment intégrer :

- cache applicatif ;
- cache SQL ;
- vues matérialisées ;
- calculs distribués ;
- files de messages ;
- traitements parallèles.

---

## 11. Validation

Toute optimisation fait l'objet :

- d'une mesure avant modification ;
- d'une mesure après modification ;
- d'une validation fonctionnelle ;
- d'une documentation.

Une optimisation n'est retenue que si elle apporte un bénéfice mesurable sans dégrader la qualité du code.

---

## 12. Amélioration continue

Les performances de TurfIA sont évaluées en permanence.

Les résultats de la supervision, des statistiques d'exploitation et des retours utilisateurs alimentent un processus d'amélioration continue destiné à maintenir un niveau élevé de performance tout au long de la vie du projet.
# TurfIA

## L006_ALGORITHMES_v1.0

**Version :** 1.0  
**Statut :** Validé  
**Objet :** Description des algorithmes de scoring, de classement et de décision

---

## Objectif

Ce livrable décrit les algorithmes utilisés par TurfIA pour transformer les données collectées en score de confiance, classement des partants, décision de jeu, propositions de paris et suivi de performance.

Les algorithmes doivent rester reproductibles. Toute modification de pondération ou de règle doit être versionnée et appliquée uniquement aux analyses futures.

---

## Principes algorithmiques

Les traitements TurfIA respectent les principes suivants :

- aucune donnée codée en dur ;
- calculs fondés sur des données historisées ;
- séparation entre score de course et classement des chevaux ;
- conservation des valeurs sources utilisées dans chaque analyse ;
- justification des décisions de jeu ;
- absence de modification rétroactive des résultats historiques ;
- évolution du modèle uniquement après validation statistique.

---

## Score de confiance de la course

Le score de confiance mesure la qualité de la course pour une prise de position. Il est noté de 0 à 100.

Ce score ne représente pas la probabilité qu'un cheval gagne. Il représente la qualité globale de la situation de pari.

### Interprétation

| Score | Décision | Budget de référence |
|------:|----------|--------------------:|
| 0–59 | Ne pas jouer | 0 € |
| 60–74 | Jouer prudemment | 10 € |
| 75–84 | Jouer normalement | 25 € |
| 85–100 | Opportunité forte | 50 € |

### Composantes principales

Le score de confiance repose notamment sur :

- lisibilité de la course ;
- concentration ou dispersion des favoris ;
- cohérence entre marché et presse ;
- qualité du consensus presse ;
- stabilité ou instabilité des cotes ;
- présence de value bets ;
- identification de chevaux surcotés ;
- fiabilité des données disponibles ;
- aptitude des principaux chevaux au parcours, à la distance et au terrain ;
- statistiques entraîneur ;
- statistiques jockey ou driver ;
- historique de l'hippodrome ;
- régularité récente des partants.

---

## Algorithme de pré-analyse

### Entrées

L'algorithme de pré-analyse utilise :

- les données de course ;
- la liste des partants ;
- les premières cotes disponibles ;
- les citations presse ;
- les données historiques cheval, entraîneur, jockey et hippodrome ;
- les conditions de course.

### Traitements

1. Vérifier la complétude minimale des données.
2. Normaliser les noms des chevaux, entraîneurs, jockeys et hippodromes.
3. Calculer les indicateurs par partant.
4. Mesurer la concentration des favoris.
5. Mesurer le consensus presse.
6. Comparer marché et consensus.
7. Identifier les écarts de valeur potentiels.
8. Attribuer un score individuel aux partants.
9. Calculer le score de confiance de la course.
10. Déterminer la recommandation de mise.

### Sorties

L'algorithme produit :

- score TurfIA provisoire ;
- niveau de risque ;
- ROI théorique ;
- classement complet ;
- bases ;
- chances régulières ;
- outsiders ;
- tocard spéculatif ;
- propositions de paris ;
- synthèse argumentée.

---

## Algorithme d'analyse finale

### Entrées

L'analyse finale reprend les sorties de la pré-analyse et actualise :

- dernières cotes ;
- mouvements de marché ;
- non-partants ;
- état du terrain ;
- changements de jockey ou driver ;
- informations de dernière minute.

### Traitements

1. Identifier les changements depuis la pré-analyse.
2. Retirer les non-partants.
3. Recalculer les indicateurs dépendants du nombre de partants.
4. Recalculer les mouvements de cotes.
5. Réviser les alertes de surcote et de value bet.
6. Recalculer le score de confiance.
7. Confirmer ou modifier la décision de jeu.
8. Générer les paris définitifs.

### Sorties

L'algorithme produit :

- classement définitif ;
- bases définitives ;
- chances régulières ;
- outsiders ;
- tocard ;
- score final ;
- risque final ;
- ROI théorique final ;
- budget recommandé ;
- tickets définitifs.

---

## Scoring individuel des partants

Le score individuel classe les chevaux dans une course donnée. Il ne doit pas être comparé mécaniquement entre deux courses différentes.

### Critères indicatifs

Le score individuel peut intégrer :

- forme récente ;
- régularité ;
- aptitude à la distance ;
- aptitude au terrain ;
- aptitude à l'hippodrome ;
- aptitude à la corde ;
- qualité du jockey ou driver ;
- réussite de l'entraîneur ;
- cohérence de la cote ;
- soutien de la presse ;
- évolution de la cote ;
- pénalisation ou avantage au poids si applicable.

### Catégories de sortie

Les partants sont classés en quatre catégories :

- bases ;
- chances régulières ;
- outsiders ;
- tocard spéculatif.

Un cheval peut être intéressant sans être une base si sa cote crée un intérêt de valeur mais que son risque reste élevé.

---

## Détection des value bets

Un value bet est un cheval dont la cote paraît supérieure à son potentiel réel estimé par TurfIA.

### Signaux possibles

- cheval bien classé par TurfIA mais moins soutenu par le marché ;
- forte citation presse avec cote encore élevée ;
- aptitude favorable non reflétée par la cote ;
- historique positif sur hippodrome, distance ou terrain ;
- mouvement de cote tardif favorable.

### Règle de prudence

Un value bet ne déclenche pas automatiquement un pari. Il doit être cohérent avec le score global de la course et la stratégie de mise.

---

## Détection des chevaux surcotés

Un cheval est considéré comme surcoté lorsque son niveau de soutien marché ou presse paraît excessif au regard des critères objectifs.

### Signaux possibles

- cote très basse sans avantage objectif suffisant ;
- forte popularité presse mais aptitude défavorable ;
- baisse de cote rapide non confirmée par les autres critères ;
- musique flatteuse mais conditions du jour défavorables ;
- jockey ou entraîneur attractif masquant une incertitude sportive.

Les chevaux surcotés peuvent être exclus des bases ou utilisés avec prudence dans les combinaisons.

---

## Calcul du ROI théorique

Le ROI théorique est une estimation prudente de l'intérêt financier d'une course avant résultat.

Il ne doit pas être confondu avec le ROI réalisé.

### Formule générale

```text
ROI théorique = (gain espéré - mise recommandée) / mise recommandée
```

Lorsque la mise recommandée est nulle, le ROI théorique n'est pas calculé et la décision est « ne pas jouer ».

### Usage

Le ROI théorique sert à comparer les courses entre elles et à documenter la décision. Il ne justifie jamais une augmentation de mise après une perte.

---

## Gestion des mises

La mise dépend exclusivement du score final de la course.

| Score | Mise maximale recommandée |
|------:|--------------------------:|
| <60 | 0 € |
| 60–74 | 10 € |
| 75–84 | 25 € |
| ≥85 | 50 € |

Règles :

- ne jamais augmenter les mises après une perte ;
- ne pas dépasser le budget associé au score ;
- privilégier la régularité de la méthode ;
- tracer chaque pari proposé et son résultat.

---

## Types de paris privilégiés

Les algorithmes de génération de tickets privilégient :

- Simple Gagnant ;
- Simple Placé ;
- Couplé Gagnant ;
- Couplé Placé ;
- 2 sur 4 ;
- Quinté Flexi.

Le choix du type de pari dépend :

- du score de confiance ;
- du niveau de dispersion des favoris ;
- du nombre de bases solides ;
- de la présence d'outsiders exploitables ;
- du budget recommandé.

---

## Contrôle des résultats

L'algorithme de contrôle compare les paris proposés à l'arrivée officielle.

### Entrées

- analyse finale ;
- tickets proposés ;
- arrivée officielle ;
- rapports PMU ;
- non-partants éventuels ;
- budget recommandé.

### Calculs

```text
profit = gains - mise
ROI course = profit / mise
ROI cumulé = profit cumulé / mise cumulée
```

Si aucune mise n'a été recommandée, la course est comptabilisée comme évitée et n'entre pas dans le ROI des courses jouées.

### Sorties

- gains ;
- profit ou perte ;
- ROI de la course ;
- ROI cumulé ;
- réussite ou échec des bases ;
- réussite ou échec des outsiders ;
- analyse critique.

---

## Validation des évolutions du modèle

Une évolution d'algorithme ne peut être validée qu'après comparaison historique.

Elle doit préciser :

- la version du modèle ;
- la règle modifiée ;
- la justification ;
- le périmètre de test ;
- l'impact sur le ROI historique simulé ;
- la date d'entrée en vigueur.

Les résultats historiques réels ne sont jamais modifiés rétroactivement.

---

## Données manquantes

Lorsqu'une donnée nécessaire est absente, TurfIA doit :

1. signaler la donnée manquante ;
2. indiquer si l'absence bloque l'analyse ;
3. appliquer une règle de prudence si l'analyse reste possible ;
4. tracer l'incertitude dans l'analyse produite.

Aucune donnée ne doit être inventée.

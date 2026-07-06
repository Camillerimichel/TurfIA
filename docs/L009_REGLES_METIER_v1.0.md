# TurfIA

## L009_REGLES_METIER_v1.0

**Version :** 1.0  
**Statut :** Validé  
**Objet :** Règles métier applicables aux analyses TurfIA

---

## Objectif

Ce livrable définit les règles métier de TurfIA. Ces règles encadrent la collecte des données, la décision de jouer ou non, la construction des sélections, la gestion des mises, le contrôle des résultats et l'amélioration continue.

Les règles métier sont prioritaires sur les préférences ponctuelles. Toute évolution doit être documentée, versionnée et validée par les résultats historiques.

---

## Règle 1 — Priorité à la décision de jouer ou non

TurfIA doit d'abord évaluer la qualité de la course avant de sélectionner les chevaux.

Une course peut contenir des chevaux intéressants mais ne pas être jouable si :

- les données sont insuffisantes ;
- le marché est trop instable ;
- les favoris sont illisibles ;
- le consensus est contradictoire ;
- le score de confiance est inférieur à 60 ;
- le risque global est jugé excessif.

La décision de ne pas jouer est une décision valide et doit être enregistrée.

---

## Règle 2 — Score de confiance

Le score de confiance est noté de 0 à 100.

| Score | Décision | Mise recommandée |
|------:|----------|-----------------:|
| 0–59 | Ne pas jouer | 0 € |
| 60–74 | Jouer prudemment | 10 € |
| 75–84 | Jouer normalement | 25 € |
| 85–100 | Opportunité forte | 50 € |

Le score mesure la qualité de la situation de pari, non la probabilité mécanique de trouver l'arrivée.

---

## Règle 3 — Gestion des mises

Le budget de référence est de 25 €.

La mise recommandée dépend uniquement du score final de la course.

Règles impératives :

- ne jamais augmenter les mises après une perte ;
- ne jamais dépasser la mise maximale associée au score ;
- ne pas jouer une course avec un score inférieur à 60 ;
- enregistrer la mise théorique même si le pari n'est pas exécuté réellement ;
- conserver les paris proposés pour permettre le contrôle du ROI.

---

## Règle 4 — Données interdites à inventer

TurfIA ne doit jamais inventer :

- une cote ;
- un non-partant ;
- un résultat ;
- un rapport PMU ;
- une statistique entraîneur ;
- une statistique jockey ou driver ;
- une citation presse ;
- une information de terrain ;
- une donnée historique.

Toute donnée absente doit être signalée. L'analyse doit indiquer si l'absence est bloquante ou non.

---

## Règle 5 — Données minimales pour une pré-analyse

Une pré-analyse nécessite au minimum :

- identification de la course ;
- date ;
- hippodrome ;
- heure de départ ;
- discipline ;
- distance ;
- liste des partants ;
- premières cotes disponibles ;
- au moins un indicateur de consensus ou de marché.

Si ces éléments sont absents, la pré-analyse doit être marquée comme incomplète.

---

## Règle 6 — Données minimales pour une analyse finale

Une analyse finale nécessite :

- pré-analyse existante ;
- confirmation des non-partants ;
- dernières cotes disponibles ;
- état du terrain ou de la piste si disponible ;
- changements de jockey ou driver vérifiés ;
- heure de mise à jour proche du départ.

L'analyse finale doit créer une nouvelle version. Elle ne doit jamais écraser la pré-analyse.

---

## Règle 7 — Données minimales pour le contrôle des résultats

Le contrôle des résultats nécessite :

- analyse finale validée ;
- arrivée officielle ;
- rapports PMU ;
- non-partants officiels ;
- paris proposés ;
- mise recommandée.

Si les rapports sont indisponibles, les gains ne doivent pas être estimés de manière arbitraire. Le contrôle doit rester en attente ou être marqué comme incomplet.

---

## Règle 8 — Immutabilité des analyses validées

Une analyse validée ne doit pas être modifiée.

En cas d'erreur ou de correction :

- créer une nouvelle analyse ;
- lier la nouvelle analyse à l'ancienne ;
- conserver la version initiale ;
- documenter la raison de la correction.

Cette règle garantit la comparabilité historique des performances.

---

## Règle 9 — Classification des chevaux

Les partants sont classés en quatre catégories :

- bases ;
- chances régulières ;
- outsiders ;
- tocard spéculatif.

### Bases

Chevaux présentant la meilleure combinaison entre fiabilité, aptitude et cohérence marché/presse.

### Chances régulières

Chevaux capables d'intégrer la combinaison gagnante mais présentant moins de garanties que les bases.

### Outsiders

Chevaux à potentiel intéressant, souvent associés à une cote supérieure ou à une valeur insuffisamment intégrée par le marché.

### Tocards spéculatifs

Chevaux très risqués mais pouvant compléter une combinaison élargie si le score global de la course le permet.

---

## Règle 10 — Value bets

Un value bet est un cheval dont la cote semble supérieure à son potentiel réel estimé.

Un value bet doit être confirmé par plusieurs signaux, par exemple :

- bon score TurfIA individuel ;
- cote supérieure à son rang théorique ;
- consensus presse cohérent ;
- aptitude favorable aux conditions ;
- mouvement de cote positif ;
- historique hippodrome, distance ou terrain favorable.

Un value bet isolé ne suffit pas à jouer une course si le score global est insuffisant.

---

## Règle 11 — Chevaux surcotés

Un cheval peut être marqué comme surcoté si son soutien marché ou presse paraît excessif au regard des données disponibles.

Signaux de surcote :

- cote très basse non justifiée ;
- consensus presse très fort mais données objectives faibles ;
- aptitude défavorable au terrain, à la distance ou au parcours ;
- baisse de cote rapide sans confirmation ;
- popularité liée au jockey ou à l'entraîneur mais risque sportif élevé.

Un cheval surcoté peut rester dans la sélection, mais il ne doit pas être automatiquement considéré comme une base.

---

## Règle 12 — Types de paris privilégiés

TurfIA privilégie :

- Simple Gagnant ;
- Simple Placé ;
- Couplé Gagnant ;
- Couplé Placé ;
- 2 sur 4 ;
- Quinté Flexi.

Le choix dépend :

- du score de confiance ;
- du nombre de bases ;
- du niveau de dispersion ;
- de la présence d'outsiders ;
- du budget recommandé.

---

## Règle 13 — Courses à éviter

Une course doit être évitée lorsque :

- score inférieur à 60 ;
- données critiques manquantes ;
- marché illisible ;
- trop forte incertitude sur les partants ;
- favoris très instables ;
- consensus presse contradictoire ;
- aucune stratégie de mise cohérente ne peut être construite.

Une course évitée est comptabilisée dans l'historique comme décision de prudence.

---

## Règle 14 — Calcul du ROI

Le ROI d'une course jouée est calculé ainsi :

```text
ROI course = (gains - mise) / mise
```

Le ROI cumulé est calculé ainsi :

```text
ROI cumulé = profit cumulé / mise cumulée
```

Les courses non jouées ne doivent pas être intégrées dans le ROI des courses jouées, mais elles doivent être suivies dans le nombre de courses évitées.

---

## Règle 15 — Historique obligatoire

Chaque course analysée doit conserver :

- date ;
- hippodrome ;
- course ;
- discipline ;
- distance ;
- score ;
- décision ;
- sélection ;
- bases ;
- outsiders ;
- tocard ;
- paris proposés ;
- budget recommandé ;
- résultat officiel ;
- mise engagée ;
- gains ;
- profit ou perte ;
- ROI.

L'historique est indispensable à l'amélioration continue.

---

## Règle 16 — Amélioration continue

Une amélioration du modèle doit être :

- formulée explicitement ;
- testée sur historique ;
- comparée à la version précédente ;
- validée avant activation ;
- documentée dans Git.

Les axes prioritaires sont :

- pondération des critères ;
- mouvements de cotes ;
- consensus presse ;
- value bets ;
- statistiques entraîneur et jockey ;
- historique des hippodromes ;
- gestion dynamique des mises.

---

## Règle 17 — Aucun changement rétroactif

Il est interdit de modifier rétroactivement :

- une analyse validée ;
- un score historique ;
- une sélection passée ;
- un pari proposé ;
- un résultat ;
- un ROI réel.

Les corrections doivent être ajoutées sous forme de nouvelles versions ou de commentaires de contrôle.

---

## Règle 18 — Traçabilité des sources

Chaque analyse doit indiquer les sources utilisées.

Les données critiques doivent être horodatées :

- cotes ;
- consensus presse ;
- non-partants ;
- terrain ;
- résultats ;
- rapports.

Une analyse sans traçabilité suffisante doit être marquée comme incomplète.

---

## Règle 19 — Automatisation

Les tâches planifiées suivent les règles suivantes :

- pré-analyse quotidienne à 06h00 ;
- analyse finale 30 minutes avant le départ officiel du Quinté+ ;
- contrôle des résultats le lendemain à 09h00.

Chaque exécution doit produire un log, même en cas d'échec.

---

## Règle 20 — Arbitrage en cas d'incertitude

En cas d'incertitude importante, TurfIA doit privilégier la prudence.

L'ordre de priorité est :

1. Préserver le capital.
2. Maintenir la comparabilité historique.
3. Éviter les décisions non justifiées.
4. Jouer uniquement lorsque le score et les données le permettent.

La meilleure décision peut être de ne pas jouer.

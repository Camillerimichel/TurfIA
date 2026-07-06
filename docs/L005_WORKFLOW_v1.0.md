# TurfIA

## L005_WORKFLOW_v1.0

**Version :** 1.0  
**Statut :** Validé  
**Objet :** Description du cycle opérationnel quotidien TurfIA

---

## Objectif

Ce livrable décrit le workflow opérationnel de TurfIA. Il définit l'enchaînement des traitements permettant de passer d'une course identifiée à une décision de jeu, puis au contrôle objectif du résultat et à la mise à jour de l'historique.

Le workflow est construit pour garantir :

- la reproductibilité des analyses ;
- la traçabilité des décisions ;
- la séparation entre pré-analyse, analyse finale et contrôle ;
- la conservation des versions successives ;
- la mesure permanente du ROI.

---

## Principes généraux

Le cycle TurfIA repose sur cinq étapes :

1. Pré-analyse.
2. Analyse finale.
3. Contrôle des résultats.
4. Mise à jour de l'historique.
5. Amélioration continue.

Chaque étape doit produire une sortie enregistrée. Aucune analyse ne doit être écrasée rétroactivement. Toute modification du modèle doit être documentée, versionnée et appliquée uniquement aux analyses futures.

---

## Étape 1 — Pré-analyse

### Moment d'exécution

La pré-analyse est exécutée quotidiennement à 06h00.

### Objectif

Identifier la course support du Quinté+ et produire une première évaluation de l'intérêt de jouer la course.

La priorité n'est pas de sélectionner immédiatement les chevaux mais de déterminer si la course présente une qualité suffisante pour engager une mise.

### Données collectées

Pour la course :

- date ;
- hippodrome ;
- nom de la course ;
- numéro de course ;
- heure officielle ;
- discipline ;
- distance ;
- corde ;
- surface ;
- état de la piste ou du terrain ;
- allocation ;
- conditions de course ;
- nombre de partants.

Pour chaque partant :

- numéro ;
- nom ;
- entraîneur ;
- jockey ou driver ;
- musique ;
- valeur handicap si disponible ;
- cote PMU ;
- principales cotes concurrentes si disponibles ;
- évolution des cotes ;
- consensus presse ;
- pourcentage de citations ;
- indicateurs d'aptitude au parcours, à la distance et au terrain.

### Analyses produites

La pré-analyse évalue notamment :

- la concentration des favoris ;
- le niveau de consensus presse ;
- la cohérence entre marché et presse ;
- les mouvements de cotes ;
- les chevaux susceptibles d'être sous-cotés ;
- les chevaux susceptibles d'être surcotés ;
- l'aptitude au parcours ;
- l'aptitude à la distance ;
- l'aptitude au terrain ;
- les statistiques entraîneur ;
- les statistiques jockey ou driver ;
- l'historique de l'hippodrome.

### Sorties attendues

La pré-analyse produit :

- un score TurfIA provisoire ;
- un niveau de risque ;
- un ROI théorique ;
- une décision provisoire : ne pas jouer, jouer prudemment, jouer normalement ou opportunité forte ;
- un classement complet des partants ;
- les bases ;
- les chances régulières ;
- les outsiders ;
- un tocard spéculatif ;
- des propositions de paris adaptées au budget ;
- une synthèse argumentée.

La version produite est enregistrée comme référence de pré-analyse.

---

## Étape 2 — Analyse finale

### Moment d'exécution

L'analyse finale est exécutée environ 30 minutes avant l'heure officielle de départ du Quinté+.

### Objectif

Actualiser les données sensibles au temps et produire la décision définitive de jeu.

### Données actualisées

L'analyse finale doit vérifier :

- les dernières cotes disponibles ;
- les mouvements de marché récents ;
- les non-partants ;
- l'état actualisé du terrain ;
- les changements de jockey ou driver ;
- les informations de dernière minute ;
- les écarts entre la pré-analyse et les données finales.

### Traitements

Le moteur TurfIA recalcule :

- le consensus ;
- les signaux de marché ;
- les alertes de surcote ou de sous-cote ;
- le score TurfIA ;
- le risque ;
- le ROI théorique ;
- la stratégie de mise.

### Sorties attendues

L'analyse finale produit :

- le classement définitif ;
- les bases définitives ;
- les chances régulières ;
- les outsiders ;
- le tocard ;
- les paris définitifs ;
- la mise recommandée ;
- la justification de la décision finale.

La version finale est enregistrée séparément de la pré-analyse.

---

## Étape 3 — Contrôle des résultats

### Moment d'exécution

Le contrôle des résultats est exécuté le lendemain à 09h00 sur la course analysée la veille.

### Objectif

Comparer les décisions TurfIA à l'arrivée officielle et mesurer la performance réelle.

### Données récupérées

Le contrôle récupère :

- l'arrivée officielle ;
- les rapports PMU ;
- les non-partants éventuels ;
- les paris réellement proposés ;
- la mise théorique recommandée ;
- les gains calculés selon les rapports officiels.

### Calculs

Le contrôle calcule :

- le gain brut ;
- le profit ou la perte ;
- le ROI de la course ;
- le ROI cumulé ;
- le taux de réussite ;
- le ROI par type de pari ;
- le ROI par tranche de confiance.

### Sorties attendues

Le contrôle produit :

- une comparaison entre sélection et arrivée officielle ;
- le bilan financier de la course ;
- l'impact sur le ROI cumulé ;
- une analyse critique des réussites et erreurs ;
- les pistes d'amélioration à tester.

---

## Étape 4 — Mise à jour de l'historique

Après chaque contrôle, TurfIA met à jour l'historique sans modifier les analyses passées.

Les éléments conservés sont notamment :

- date ;
- hippodrome ;
- course ;
- discipline ;
- distance ;
- score TurfIA ;
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

---

## Étape 5 — Amélioration continue

L'amélioration continue ne modifie jamais les résultats historiques.

Elle consiste à analyser les écarts entre prévision et résultat afin d'identifier les paramètres pouvant être améliorés :

- pondération des critères ;
- interprétation des mouvements de cotes ;
- qualité du consensus presse ;
- identification des value bets ;
- statistiques entraîneur et jockey ;
- historique par hippodrome ;
- gestion dynamique des mises.

Toute évolution du modèle doit être documentée, versionnée et validée par comparaison historique avant usage opérationnel.

---

## Règles de blocage

Une analyse ne doit pas être finalisée si l'un des éléments suivants est absent ou incohérent :

- absence de course identifiée ;
- nombre de partants non fiable ;
- données de cotes indisponibles ;
- non-partants non vérifiés avant l'analyse finale ;
- résultat officiel non confirmé pour le contrôle ;
- impossibilité de calculer les rapports ou les gains.

Dans ce cas, le statut du traitement doit être marqué comme incomplet et justifié.

---

## Traçabilité

Chaque étape doit enregistrer :

- l'heure d'exécution ;
- la source des données utilisées ;
- la version du modèle ;
- les paramètres de scoring ;
- les sorties produites ;
- les erreurs ou données manquantes ;
- le statut du traitement.

La traçabilité est une condition nécessaire à la comparabilité des performances dans le temps.

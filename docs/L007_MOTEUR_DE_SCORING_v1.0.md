L007 — Moteur de scoring TurfIA

## Objectif
Définir les règles de calcul du score TurfIA et de la confiance associée.

## Critères principaux
- Consensus presse
- Évolution des cotes
- Value bet
- Aptitude distance
- Aptitude parcours
- Aptitude terrain
- Forme récente
- Statistiques entraîneur
- Statistiques jockey/driver
- Historique hippodrome

## Normalisation
Chaque critère est converti sur une échelle de 0 à 100 avant pondération.
Les données absentes sont neutralisées sans pénaliser artificiellement le score.

## Calcul
Score final = somme des critères pondérés.
Les pondérations sont stockées en configuration et versionnées.

## Décision
0-59 : aucune mise.
60-74 : budget réduit.
75-84 : budget nominal.
85-100 : budget renforcé.

## Principes
- Validation statistique avant toute modification.
- Historisation des versions du modèle.
- Aucune modification rétroactive des résultats historiques.
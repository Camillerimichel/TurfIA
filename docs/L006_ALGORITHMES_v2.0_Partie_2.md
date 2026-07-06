# L006_ALGORITHMES_v2.0.md --- Partie 2/3

# 5. Orchestration des calculs

Le moteur exécute les traitements selon un ordre strict garantissant la
reproductibilité des résultats. Chaque étape consomme uniquement les
données produites par l'étape précédente.

``` mermaid
flowchart TD
VAL[Validation]
NORM[Normalisation]
MET[Calcul des métriques]
RULES[Règles métier]
SCORE[Score TurfIA]
REC[Recommandations]

VAL --> NORM
NORM --> MET
MET --> RULES
RULES --> SCORE
SCORE --> REC
```

# 6. Décisions d'architecture

## ADR-001 --- Déterminisme

**Contexte** : la confiance dans le système repose sur la capacité à
rejouer un calcul et obtenir le même résultat.
**Décision** : les calculs ne dépendent d'aucun état interne non
persistant (pas d'horloge système, pas de générateur aléatoire non
tracé, pas de cache non versionné).
**Conséquences** : toute source de variabilité (ex. ordre d'itération
non déterministe) doit être explicitement contrôlée dans le code.

## ADR-002 --- Paramétrage

**Contexte** : les pondérations du modèle de scoring évoluent à mesure
que la méthode s'affine (cf. L031.7 Amélioration continue).
**Décision** : les pondérations sont externalisées afin de permettre
leur évolution sans modifier le code.
**Conséquences** : nécessite un mécanisme de configuration versionné
(cf. L026) distinct du code source.

## ADR-003 --- Versionnement

**Contexte** : deux analyses produites à des dates différentes peuvent
utiliser des règles différentes.
**Décision** : chaque exécution est associée à une version des règles
métier garantissant la comparabilité historique.
**Conséquences** : le modèle de données doit porter cette version sur
chaque résultat historisé (cf. L004 §5, L011).

## ADR-004 --- Absence d'apprentissage en ligne

**Contexte** : un modèle qui s'auto-modifie en production romprait le
déterminisme et l'auditabilité.
**Décision** : le moteur n'effectue aucun réentraînement automatique en
production ; toute évolution du modèle de scoring est un changement de
version explicite et documenté (cf. L031.7).
**Conséquences** : l'amélioration continue est un processus périodique
et gouverné, non un mécanisme temps réel.

# 7. Gestion des anomalies

Les erreurs détectées interrompent uniquement le calcul concerné. Les
informations de diagnostic sont journalisées afin de permettre une
reprise contrôlée.

## 7.1 Typologie des anomalies de calcul

  Type d'anomalie                     Traitement                                   Document
  ------------------------------------- --------------------------------------------- ------------------
  Donnée manquante non critique          Calcul avec indicateur de confiance réduit    L031.1
  Donnée manquante critique              Interruption du calcul pour ce partant         L023
  Valeur hors intervalle attendu          Rejet et journalisation, alerte si récurrent  L023, L035
  Erreur de configuration (pondération)    Interruption du batch, alerte immédiate       L026, L035

*Fin de la partie 2/3.*

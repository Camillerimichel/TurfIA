# L009_REGLES_METIER_v2.0.md --- Partie 1/2

# 1. Objet

Ce document présente l'architecture des règles métier de TurfIA. Il
décrit leur rôle dans le système, leur organisation et les principes
permettant de garantir des décisions cohérentes, explicables et
reproductibles.

# 2. Principes

Les règles métier sont indépendantes de l'interface utilisateur, de
l'API et de la base de données. Elles constituent le référentiel
fonctionnel utilisé par le moteur d'analyse.

Les principes retenus sont :

-   centralisation des règles ;
-   paramétrage lorsque cela est pertinent ;
-   versionnement ;
-   traçabilité ;
-   reproductibilité.

## 2.1 Nature d'une règle métier chez TurfIA

Une règle métier est une fonction déterministe prenant en entrée des
données validées et produisant en sortie une décision ou une valeur,
accompagnée de sa justification. Une règle métier ne réalise jamais
d'entrée-sortie (I/O) directe : elle ne lit ni n'écrit en base, ne fait
aucun appel réseau. Cette propriété est ce qui rend les règles
testables unitairement et rejouables (cf. L020).

# 3. Organisation

``` mermaid
flowchart LR
Data[Données] --> Rules[Règles métier]
Rules --> Engine[Moteur TurfIA]
Engine --> Decision[Décision]
Decision --> History[Historisation]
```

# 4. Domaines

  Domaine          Finalité
  ---------------- ----------------------
  Validation       Contrôle des données
  Qualification    Analyse de la course
  Scoring          Calcul des scores
  Recommandation   Sélection des paris
  Contrôle         Calcul du ROI

## 4.1 Exemples de règles par domaine (illustratif)

  Domaine           Exemple de règle                                        Type de sortie
  ------------------ --------------------------------------------------------- ------------------
  Validation          Un partant sans cote connue à la clôture est-il exclu ?   Booléen + motif
  Qualification        La course dispose-t-elle d'un historique suffisant ?      Score de confiance
  Scoring              Quel poids relatif accorder à la forme récente ?           Valeur numérique (cf. L031.2)
  Recommandation        La combinaison risque/ROI théorique justifie-t-elle une proposition ?  Décision + justification
  Contrôle              Le résultat réel correspond-il à la recommandation ?      Écart mesuré

Le détail exhaustif des règles (paramètres, seuils, formules) est
spécifié dans la série L031.x ; ce document ne fixe que leur
organisation architecturale.

*Fin de la partie 1/2.*

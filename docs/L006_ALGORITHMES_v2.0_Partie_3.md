# L006_ALGORITHMES_v2.0.md --- Partie 3/3

# 8. Exigences non fonctionnelles

Le moteur d'analyse doit garantir :

-   des temps d'exécution prévisibles ;
-   une consommation maîtrisée des ressources ;
-   une reproductibilité complète ;
-   une traçabilité de chaque calcul ;
-   une évolutivité des modèles de scoring.

Toutes les optimisations doivent préserver les résultats fonctionnels.

## 8.1 Cibles mesurables

  Exigence                        Indicateur                              Cible
  --------------------------------- ----------------------------------------- ------------------
  Temps d'exécution du batch quotidien Durée totale du cycle d'analyse          Cf. seuil défini en L036
  Reproductibilité                    Écart entre deux exécutions identiques   0 (résultat strictement identique)
  Traçabilité                          Analyses avec version de règles associée 100 %

## 8.2 Compromis performance / exactitude

Aucune approximation numérique (arrondi, échantillonnage) n'est
introduite dans le seul but d'améliorer la performance sans validation
explicite de son impact sur le score final. Tout compromis de ce type
est documenté comme ADR local dans L031.x et validé par comparaison sur
historique (cf. L020).

# 9. Interactions

Le moteur d'analyse interagit avec :

-   les référentiels ;
-   les services métier ;
-   les règles métier ;
-   la base SQL ;
-   les traitements planifiés.

Il ne dialogue jamais directement avec l'interface utilisateur.

## 9.1 Hypothèses et dépendances

Le moteur suppose que les référentiels et données validées lui sont
fournis complets et cohérents par les étapes amont du workflow (cf.
L005 §4.2) : il ne réalise pas lui-même de collecte ni de
correction de données source.

# 10. Références

Les mécanismes présentés sont détaillés dans :

-   L005 : Workflow ;
-   L007 : API ;
-   L008 : Base SQL ;
-   L009 : Règles métier ;
-   L031 : Spécifications algorithmiques.

## Historique

  Version   Description
  --------- ----------------------------------------------------
  1.0       Version initiale
  2.0       Réécriture orientée Software Architecture Document
  2.1       Enrichissement industriel : contrats d'entrée/sortie par module, ADR détaillées, typologie des anomalies de calcul, cibles mesurables, compromis performance/exactitude, hypothèses et dépendances

*Fin du document L006.*

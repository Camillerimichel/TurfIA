# L004_MODELE_DE_DONNEES_v2.0.md --- Partie 1/2

# 1. Objet

Ce document présente l'architecture logique du modèle de données de
TurfIA. Il décrit les domaines fonctionnels, les principes de
modélisation et les responsabilités des principales entités sans
détailler le schéma physique, documenté dans les spécifications
techniques.

# 2. Principes de modélisation

Le modèle de données repose sur les principes suivants :

-   séparation entre référentiels et données d'exploitation ;
-   intégrité référentielle systématique ;
-   historisation des traitements ;
-   absence de redondance fonctionnelle ;
-   extensibilité des structures.

# 3. Domaines de données

  Domaine          Finalité
  ---------------- --------------------------------------------
  Référentiels     Chevaux, jockeys, entraîneurs, hippodromes
  Courses          Réunions, courses et partants
  Analyses         Pré-analyses, analyses finales, scores
  Résultats        Arrivées officielles, rapports et ROI
  Administration   Paramètres, journaux et supervision

``` mermaid
erDiagram
REFERENTIELS ||--o{ COURSES : utilise
COURSES ||--o{ ANALYSES : produit
ANALYSES ||--o{ RESULTATS : compare
RESULTATS ||--o{ HISTORIQUE : alimente
```

# 4. Responsabilités

Chaque domaine possède son propre cycle de vie et peut évoluer
indépendamment tant que les contrats de données sont respectés.

*Fin de la partie 1/2.*

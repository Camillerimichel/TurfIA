# L004_MODELE_DE_DONNEES_v2.0.md --- Partie 1/2

# 1. Objet

Ce document présente l'architecture logique du modèle de données de
TurfIA. Il décrit les domaines fonctionnels, les principes de
modélisation et les responsabilités des principales entités sans
détailler le schéma physique, documenté dans les spécifications
techniques (L011 Schéma SQL, L030.x Dictionnaire de données).

## 1.1 Positionnement (vue informationnelle)

Ce document constitue la **vue informationnelle** du SAD au sens
ISO/IEC/IEEE 42010 : il répond aux préoccupations de cohérence,
d'intégrité et d'évolutivité des données, indépendamment du moteur de
persistance retenu. Le choix technologique (PostgreSQL) et son schéma
physique sont traités en L008 et L011.

# 2. Principes de modélisation

Le modèle de données repose sur les principes suivants :

-   séparation entre référentiels et données d'exploitation ;
-   intégrité référentielle systématique ;
-   historisation des traitements ;
-   absence de redondance fonctionnelle ;
-   extensibilité des structures.

## 2.1 Classification des données

  Catégorie                Exemples                              Politique de conservation
  ------------------------- -------------------------------------- ----------------------------------
  Référentiels stables       Chevaux, jockeys, entraîneurs, hippodromes  Conservation indéfinie, mise à jour contrôlée
  Données d'exploitation      Réunions, courses, partants, cotes      Conservation indéfinie, append-only
  Résultats d'analyse         Scores, classements, décisions          Immuables après validation (cf. ADR-002 de L001)
  Données techniques           Journaux, paramètres, verrous          Politique de purge définie en L038

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

## 4.1 Propriétaire fonctionnel par domaine

  Domaine          Propriétaire fonctionnel        Fréquence de mise à jour
  ---------------- -------------------------------- ---------------------------
  Référentiels      Module de collecte (L009/L010)   Ponctuelle, sur détection de nouveauté
  Courses           Module de collecte                Quotidienne (avant réunion)
  Analyses           Moteur TurfIA                     À chaque cycle d'analyse
  Résultats           Module de contrôle des résultats  Après clôture de chaque course
  Administration      Exploitation                      Sur incident ou changement de configuration

## 4.2 Sensibilité et confidentialité des données

Le modèle de données ne contient pas, par conception, de données à
caractère personnel sensibles au sens RGPD (les entités concernent des
chevaux, courses et cotes, pas des utilisateurs finaux). Les comptes
d'accès à l'administration sont traités en L021 (Sécurité) et non dans
ce document.

*Fin de la partie 1/2.*

# L018 — Architecture de l'interface HTML

## 0. Métadonnées du document

| Champ | Valeur |
| --- | --- |
| Identifiant | L018 |
| Niveau documentaire | Spécification technique (cf. L001 §3) |
| Version | 1.0 |
| Documents liés | L007/L016 (API), L021/L034 (sécurité), L024/L036 (performances) |

## 1. Objectif

### 1.1 Finalité

L'interface HTML constitue l'interface utilisateur principale de TurfIA.

Elle permet :

- la consultation des données ;
- le lancement des traitements ;
- le suivi quotidien des analyses ;
- le contrôle du ROI ;
- l'administration de la plateforme.

Toute la logique métier reste implémentée dans l'API.

---

## 2. Principes d'architecture

### 2.1 Architecture générale

L'interface repose sur une architecture simple.

```text
Navigateur

      │

      ▼

Interface HTML

      │

      ▼

API REST TurfIA

      │

      ▼

Services Métier

      │

      ▼

Base SQL
```

L'interface n'accède jamais directement à la base de données.

---

### 2.2 Principes

L'interface respecte les principes suivants :

- simplicité ;
- rapidité ;
- lisibilité ;
- responsive design ;
- composants réutilisables ;
- séparation présentation / métier.

---

## 3. Organisation des répertoires

```text
html/

templates/

static/

css/

js/

images/

icons/

fonts/
```

---

### 3.1 Templates

Les modèles HTML contiennent uniquement la structure des pages.

Ils ne contiennent aucune logique métier.

---

### 3.2 CSS

Les feuilles de style regroupent :

- mise en page ;
- composants graphiques ;
- responsive design ;
- thème graphique.

---

### 3.3 JavaScript

Le code JavaScript assure uniquement :

- appels API ;
- interactions utilisateur ;
- rafraîchissement dynamique ;
- graphiques.

Les traitements métier restent dans l'API.

### 3.4 Principe de non-duplication des règles

Aucune règle de validation métier n'est réimplémentée en JavaScript
au-delà d'un confort d'expérience utilisateur immédiat (ex. désactiver
un bouton) : la validation faisant foi reste celle de l'API (cf. L016
§7.1). Toute règle dupliquée côté client doit rester strictement
équivalente à la règle serveur, afin d'éviter une divergence silencieuse.

---

## 4. Navigation

### 4.1 Structure

La navigation principale comprend les rubriques suivantes :

```text
Accueil

Quinté du jour

Pré-analyses

Analyses finales

Historique

Statistiques

Tableaux de bord

Administration
```

---

### 4.2 Navigation secondaire

Chaque module dispose de ses propres écrans.

Exemple :

```text
Courses

Partants

Analyses

Paris

Résultats
```

---

## 5. Tableau de bord

### 5.1 Objectif

Le tableau de bord constitue la page d'accueil des administrateurs.

Il présente en temps réel :

- état des automatisations ;
- Quinté du jour ;
- score TurfIA ;
- ROI global ;
- alertes ;
- supervision.

---

### 5.2 Widgets

Les principaux widgets sont :

- Course du jour ;
- Score de confiance ;
- ROI cumulé ;
- Dernières analyses ;
- Derniers contrôles ;
- Tâches automatiques ;
- Santé du système.

---

## 6. Module Courses

Ce module permet :

- consulter les réunions ;
- consulter les courses ;
- afficher les partants ;
- afficher les cotes ;
- consulter les résultats.

Chaque course possède une fiche complète.

---

## 7. Module Analyses

Chaque analyse présente notamment :

- score TurfIA ;
- classement ;
- bases ;
- outsiders ;
- tocard ;
- ROI théorique ;
- commentaires.

Les différentes versions d'une analyse restent accessibles.

---

## 8. Module Historique

L'historique permet de retrouver :

- toutes les analyses ;
- toutes les sélections ;
- tous les paris ;
- tous les résultats ;
- tous les ROI.

Des filtres permettent une recherche rapide.

---

## 9. Module Statistiques

Ce module présente notamment :

- ROI global ;
- ROI par hippodrome ;
- ROI par discipline ;
- ROI par score ;
- ROI par type de pari ;
- évolution mensuelle.

Les statistiques sont calculées automatiquement.

---

## 10. Module Administration

L'administration permet :

- consulter les journaux ;
- lancer une automatisation ;
- vérifier les sauvegardes ;
- consulter les versions ;
- gérer les paramètres ;
- contrôler la supervision.

Les fonctions sensibles sont réservées aux administrateurs.

### 10.1 Actions destructives ou sensibles

Toute action irréversible ou sensible (relance manuelle d'une
automatisation, modification d'un paramètre de production) déclenchée
depuis l'interface d'administration exige une confirmation explicite
et est journalisée avec l'identité de l'opérateur (cf. L022).

---

## 11. Composants graphiques

Les composants standards comprennent notamment :

- tableaux ;
- formulaires ;
- cartes ;
- badges ;
- graphiques ;
- notifications ;
- boîtes de dialogue.

Chaque composant est réutilisable.

---

## 12. Responsive Design

L'interface est compatible avec :

- ordinateur ;
- tablette ;
- smartphone.

Les principaux tableaux restent consultables sur les petits écrans.

---

## 13. Accessibilité

L'interface respecte les bonnes pratiques d'accessibilité :

- contrastes suffisants ;
- navigation clavier ;
- structure HTML sémantique ;
- messages d'erreur explicites ;
- tailles de police adaptées.

---

## 14. Performances

Les objectifs sont :

- chargement rapide des pages ;
- appels API limités ;
- pagination des listes ;
- chargement différé des données volumineuses ;
- mise en cache des ressources statiques.

---

## 15. Sécurité

Les mesures suivantes sont appliquées :

- authentification obligatoire pour l'administration ;
- contrôle des autorisations ;
- protection CSRF ;
- validation des données ;
- expiration des sessions ;
- journalisation des actions sensibles.

### 15.1 Renvoi vers les documents transverses

Le détail des mécanismes d'authentification et de protection est
spécifié en L021 (Sécurité) et L034 (Architecture sécurité), afin
d'éviter toute duplication de contenu susceptible de diverger.

---

## 16. Évolutivité

L'architecture retenue permet d'ajouter facilement :

- de nouveaux tableaux de bord ;
- de nouveaux graphiques ;
- de nouveaux modules fonctionnels ;
- une interface mobile dédiée ;
- un espace utilisateur personnalisé.

Cette architecture constitue la référence pour le développement de l'ensemble des interfaces HTML de TurfIA.

---

## Historique

| Version | Description |
| --- | --- |
| 1.0 | Version initiale |
| 1.1 | Enrichissement industriel : métadonnées du document, principe de non-duplication des règles métier côté client, confirmation et traçabilité des actions destructives, renvoi vers les documents transverses de sécurité |

*Fin du document L018.*
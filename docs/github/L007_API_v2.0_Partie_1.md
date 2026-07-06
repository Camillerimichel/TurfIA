# L007_API_v2.0.md --- Partie 1/3

# 1. Objet

Ce document présente l'architecture générale de l'API REST de TurfIA. Il
décrit son rôle dans l'architecture globale, les principes de conception
retenus et les responsabilités des différents domaines fonctionnels
exposés.

# 2. Principes d'architecture

L'API constitue l'unique point d'entrée des consommateurs de services.
Elle est conçue selon les principes suivants :

-   architecture REST ;
-   absence d'état côté serveur (stateless) ;
-   format d'échange JSON ;
-   versionnement explicite ;
-   validation systématique des requêtes ;
-   découplage entre présentation et logique métier.

# 3. Organisation

``` mermaid
flowchart LR
Client --> API
API --> Services
Services --> Moteur
Services --> BaseSQL
```

# 4. Domaines exposés

  Domaine          Fonction
  ---------------- -------------------------------------------
  Référentiels     Consultation des données permanentes
  Courses          Gestion des réunions, courses et partants
  Analyses         Pré-analyses et analyses finales
  Résultats        Contrôle, ROI et statistiques
  Administration   Paramètres, supervision et tâches

*Fin de la partie 1/3.*

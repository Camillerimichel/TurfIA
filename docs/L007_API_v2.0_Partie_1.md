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

## 2.1 Style d'interface et niveau de maturité Richardson

L'API vise le **niveau 2** du modèle de maturité de Richardson :
utilisation correcte des ressources (URI) et des verbes HTTP, sans
adoption complète de HATEOAS (niveau 3), jugée disproportionnée par
rapport au nombre et à la stabilité des clients actuels. Ce choix est
réévalué si de nouveaux clients autonomes (découverte dynamique de
capacités) apparaissent.

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

## 4.1 Niveau d'exposition et audience par domaine

  Domaine          Audience                        Authentification requise
  ---------------- -------------------------------- ---------------------------
  Référentiels      Clients internes et interface     Oui (lecture)
  Courses           Clients internes et interface     Oui (lecture)
  Analyses          Clients internes et interface     Oui (lecture/écriture selon rôle)
  Résultats         Clients internes et interface     Oui (lecture)
  Administration    Opérateurs habilités uniquement    Oui, rôle administrateur (cf. L021, L034)

Aucun domaine n'est exposé sans authentification, y compris en lecture
seule, conformément à L021.

*Fin de la partie 1/3.*

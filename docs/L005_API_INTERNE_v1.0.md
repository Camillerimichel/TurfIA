L005 — API interne de TurfIA

## Objectif
Définir les interfaces entre les différents modules de TurfIA.

## Principes
- API REST interne.
- Échanges JSON.
- Versionnement des endpoints.
- Authentification centralisée.

## Endpoints principaux
- POST /api/v1/collecte
- POST /api/v1/normalisation
- POST /api/v1/preanalyse
- POST /api/v1/analyse-finale
- POST /api/v1/controle
- GET /api/v1/historique/{course_id}
- GET /api/v1/statistiques

## Contrats d'échange
Chaque réponse contient : request_id, timestamp, version_api et statut.

## Authentification
- Jeton JWT interne.
- HTTPS obligatoire.
- Contrôle des rôles par service.

## Traçabilité
- Journalisation de tous les appels.
- Conservation des requêtes et réponses.
- Corrélation par request_id.
- Horodatage UTC.

## Codes de retour
200, 400, 401, 403, 404, 409, 500.
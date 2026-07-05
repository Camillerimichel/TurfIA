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

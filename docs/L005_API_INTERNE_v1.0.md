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
### POST /collecte
Entrée : date_course, reunion.
Sortie : identifiant de collecte, statut, nombre de partants.

### POST /preanalyse
Entrée : course_id.
Sortie : score_confiance, classement, bases, outsiders, tocard.

### POST /analyse-finale
Entrée : course_id.
Sortie : sélection définitive, paris recommandés, budget.

### Codes de retour
- 200 : succès
- 400 : requête invalide
- 404 : ressource absente
- 500 : erreur interne
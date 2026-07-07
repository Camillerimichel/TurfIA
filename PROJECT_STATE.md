# PROJECT_STATE

## État actuel du projet

Le SAD (`docs/`, L001-L039) est complet et enrichi au niveau industriel. Une première
implémentation verticale conforme au SAD existe désormais sur `develop` : schéma SQL,
migrations, cœur applicatif, algorithmes de scoring, un service d'orchestration et une
API REST minimale, avec tests unitaires. Vérifiée de bout en bout contre une instance
PostgreSQL locale réelle (migration, insertion, lecture via l'API).

## Implémenté

- **Arborescence** conforme à L014 (tous les répertoires du SAD existent).
- **Schéma SQL** conforme à L011 et L030.1-L030.6 : 35 tables (référentiels, métier,
  analyses, statistiques, techniques), rôles applicatifs, contraintes, index
  (`sql/schema/`). Seed des référentiels de base (`sql/seeds/`).
- **Migrations** conformes à L013 : runner (`scripts/run_migrations.py`) et migration
  initiale de création du schéma complet.
- **Core** (`src/core/`) : configuration fail-fast (L026), journalisation structurée
  JSON (L022), hiérarchie d'exceptions (L023), constantes structurelles.
- **Database** (`src/database/`) : gestion de connexion/session (L015 §4).
- **Models** (`src/models/`) : dataclasses pour les référentiels, tables métier et
  tables d'analyse (immuables).
- **Repositories** (`src/repositories/`) : référentiels, courses, analyses — SQL
  explicite et paramétré (L015 §6).
- **Algorithmes** (`src/algorithms/`) : normalisation, Score TurfIA, risque, ROI
  théorique, value bets, classement/catégorisation/budget — fonctions pures conformes
  à L031.1-L031.6, avec garde-fou anti-martingale.
- **Service** (`src/services/analyse_service.py`) : orchestre la chaîne L006 §3.
- **API** (`api/`) : FastAPI versionnée (`/api/v1`), enveloppe de réponse normalisée
  (L032.1 §6), gestion d'erreurs centralisée y compris 404/422 (L023 §4.1, L016 §7).
  Endpoints : `/system/health`, `/system/version`, `GET /hippodromes`,
  `POST/GET /reunions`, `POST/GET /reunions/{id}/courses`, `GET /courses/{id}`,
  `POST /chevaux`, `POST/GET /courses/{id}/partants`,
  `POST/GET /courses/{id}/analyses`, `GET /analyses/{id}` — le flux complet
  réunion → course → chevaux → partants → déclenchement d'analyse → relecture est
  pilotable de bout en bout via HTTP.
- **Tests** : 61 tests unitaires (algorithmes + configuration) + 7 tests
  d'intégration API (repositories en mémoire, `tests/integration/`), tous verts
  (68 au total).

## Correction notable apportée au SAD pendant l'implémentation

La table documentée `analyse` (L011 §8.3, L030.3 §3) est implémentée sous le nom
physique `analyses` : PostgreSQL réserve `ANALYSE` comme alias de la commande
`ANALYZE`, provoquant une erreur de syntaxe dès que l'identifiant est utilisé hors
position `CREATE TABLE`. Documenté dans les deux livrables concernés ; le nom
conceptuel et les colonnes `analyse_id` sont inchangés.

## Explicitement hors périmètre (travail futur, non implémenté)

- Automatisations planifiées (L017/L033) — aucun scheduler, `automations/` est un
  squelette vide.
- Interface HTML (L018) — `html/` est un squelette vide.
- Surface API encore partielle : pas de mise à jour/suppression (PUT/PATCH/DELETE)
  sur aucune ressource ; pas d'endpoints pour jockeys/entraineurs/résultats/cotes/
  statistiques/administration (cf. L032.2/L032.3 pour la liste complète cible).
- Authentification/RBAC réels (L021/L034) — aucune vérification d'identité n'est
  implémentée ; toutes les routes actuelles sont non protégées.
- Module statistiques (L030.4, L031.7) — aucun code.
- Collecte/import des données sources (L009, L010) — aucun code ; `AnalyseService`
  et `POST /courses/{id}/analyses` supposent des indicateurs déjà calculés fournis
  en entrée (sous-scores, cotes), pas de récupération automatique depuis une source
  externe.
- Validation d'existence incomplète sur les FK optionnelles : `jockey_id` et
  `entraineur_id` d'un partant ne sont pas vérifiés avant insertion (contrairement à
  `cheval_id`) ; une valeur invalide remonte aujourd'hui en erreur 500 générique
  plutôt qu'en 404 ciblé.
- CI/CD ; le `Dockerfile`/`docker-compose.yml` sont un socle minimal, non durcis pour
  la production (mots de passe par défaut, pas de secrets management réel).

## Prochaine étape

Selon la priorité métier : soit la collecte de données réelle (L009/L010) pour
alimenter le déclenchement d'analyse avec de vraies indicateurs plutôt que des
valeurs saisies à la main, soit la poursuite de l'extension de la surface API
(jockeys/entraineurs/résultats/cotes/statistiques, puis authentification réelle).

## Conventions de développement

- Commits atomiques.
- Développement sur la branche develop.
- Documentation synchronisée avec le code.
- Aucune modification rétroactive des historiques.
- Respect des procédures TurfIA.

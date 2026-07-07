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
  `POST/GET /courses/{id}/analyses`, `POST /courses/{id}/analyses/auto`,
  `GET /analyses/{id}` — le flux complet réunion → course → chevaux → partants →
  déclenchement d'analyse (manuel ou automatique depuis la collecte) → relecture est
  pilotable de bout en bout via HTTP.
- **Collecte** (`src/collecte/`) : architecture multi-sources en 4 niveaux (données
  officielles, marché, consensus presse, base TurfIA propriétaire). Registre
  déclaratif de 12 sources (`src/collecte/registre.py`) avec statut vérifié par accès
  réseau réel le 2026-07-07 :
  | Source | Niveau | Statut |
  | --- | --- | --- |
  | PMU | 1 (officiel) + 2 (marché) | **Implémentée** (`src/collecte/pmu/`) |
  | France Galop | 1 | Non implémentée — site atteignable (HTTP 301), structure non explorée |
  | LeTROT | 1 | Non implémentée — protection anti-bot (HTTP 403) |
  | ZEbet, Genybet, Unibet, Betclic | 2 | Non implémentées — non explorées |
  | Paris-Turf | 3 | Non implémentée — site atteignable (HTTP 200), structure non explorée |
  | Geny | 3 | Non implémentée — limitation immédiate (HTTP 429) |
  | Canalturf, ZEturf | 3 | Non implémentées — non explorées |

  `CollecteService.collecter_programme_du_jour(jour)` : programme + participants PMU
  → référentiels (hippodrome/discipline/surface/état de piste/distance),
  réunion/course/partant, cheval/jockey/entraineur, cote directe, résultat si
  disponible — tout en get-or-create idempotent. Script manuel
  `scripts/collecter_programme.py --date DDMMYYYY`. Aucune tâche planifiée
  (L017/L033 hors périmètre).
- **Indicateurs réels** (`src/algorithms/indicateurs.py`) : sous-scores Marché
  (probabilité implicite du marché, marge neutralisée, normalisée sur le champ) et
  Forme (moyenne normalisée des dernières positions, format « musique » PMU parsé et
  vérifié sur données réelles) ; approximation partielle du risque par la taille du
  champ. `PreparationDonneesService.preparer_donnees_partants(course_id)`
  (`src/services/preparation_service.py`) construit ces indicateurs à partir des
  données déjà collectées et les met en forme pour `AnalyseService` — exclut les
  non-partants et les partants sans cote collectée plutôt que d'inventer une valeur.
  Exposé via `POST /courses/{id}/analyses/auto` et `scripts/analyser_course.py
  --course-id N` : la boucle collecte → indicateurs → analyse est désormais complète
  et automatique, sans saisie manuelle.
- **Tests** : 61 tests unitaires (algorithmes + configuration) + 14 tests unitaires
  (mappers PMU) + 12 tests unitaires (indicateurs Marché/Forme/risque) + 10 tests
  d'intégration API (repositories en mémoire, `tests/integration/`), tous verts
  (107 au total).

## Correction notable apportée au SAD pendant l'implémentation

La table documentée `analyse` (L011 §8.3, L030.3 §3) est implémentée sous le nom
physique `analyses` : PostgreSQL réserve `ANALYSE` comme alias de la commande
`ANALYZE`, provoquant une erreur de syntaxe dès que l'identifiant est utilisé hors
position `CREATE TABLE`. Documenté dans les deux livrables concernés ; le nom
conceptuel et les colonnes `analyse_id` sont inchangés.

`src/collecte/` n'était pas anticipé dans L014 (arborescence) — ajouté avec une note
explicite dans L014 §6.1.1.

## Cadrage sur la collecte PMU (transparence, pas un refus)

L'adaptateur PMU utilise une API interne (non documentée publiquement pour un usage
tiers, mais utilisée par le site/l'application PMU eux-mêmes, accessible sans
authentification). Usage prévu : personnel, non commercial, volume faible
(déclenchement manuel, pas de cron). Le respect des CGU du site PMU reste la
responsabilité de l'utilisateur pour son usage ; le client applique par défaut un
délai de politesse entre requêtes (`DELAI_ENTRE_APPELS_SECONDES`, cf.
`src/collecte/pmu/client.py`) et un `User-Agent` explicite.

## Limites connues de la collecte (documentées, pas cachées)

- `corde` par course non collecté : le schéma ne porte `corde_id` qu'au niveau
  `hippodrome` (cf. L011/L030.1), alors que PMU le fournit par course — nécessiterait
  une migration de schéma, hors périmètre de cette tranche.
- `get_or_create_cheval/jockey/entraineur` par nom sont non atomiques (SELECT puis
  INSERT, cf. L030.2 absence de contrainte UNIQUE) — acceptable pour un script manuel
  non concurrent, à revoir si la collecte devient concurrente ou planifiée.
- Aucun historique d'évolution des cotes n'est conservé au-delà de la dernière cote
  directe collectée à chaque exécution (plusieurs exécutions dans la journée créent
  bien plusieurs lignes `cote`, cf. L011 §15, mais sans polling automatique).
- Niveau 3 (consensus presse) non implémenté : aucune source presse n'a été vérifiée
  en profondeur ; la famille de critères « Presse » de `src/algorithms/score.py`
  (`PONDERATIONS_PAR_DEFAUT["presse"]`) doit donc être alimentée manuellement pour
  l'instant.

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
- Collecte de niveau 1/2 partiellement implémentée (PMU uniquement, cf. ci-dessus).
- Seuls les sous-scores Marché et Forme sont calculés automatiquement depuis les
  données collectées (cf. `PreparationDonneesService`). Les familles Professionnels
  (statistiques jockey/entraineur), Historique (hippodrome/distance) et Aptitude
  (terrain) documentées en L031.2 §3 nécessitent des requêtes d'agrégation
  supplémentaires, non construites dans cette tranche. Le risque de la course n'est
  approximé que par la taille du champ (`calculer_indicateur_risque_taille_champ`) ;
  les autres facteurs de risque documentés (volatilité du marché, désaccord presse,
  changement de terrain, cf. L031.3 §3) restent hors périmètre.
- Niveau 3 (consensus presse) non implémenté (cf. limites connues ci-dessus) : la
  famille de critères « Presse » n'est donc alimentée par aucun indicateur réel.
- Validation d'existence incomplète sur les FK optionnelles : `jockey_id` et
  `entraineur_id` d'un partant ne sont pas vérifiés avant insertion (contrairement à
  `cheval_id`) ; une valeur invalide remonte aujourd'hui en erreur 500 générique
  plutôt qu'en 404 ciblé.
- CI/CD ; le `Dockerfile`/`docker-compose.yml` sont un socle minimal, non durcis pour
  la production (mots de passe par défaut, pas de secrets management réel).

## Prochaine étape

Selon la priorité métier : exploration d'une deuxième source niveau 1 (France Galop)
ou niveau 3 (Paris-Turf, pour sortir du mono-source PMU et alimenter enfin la famille
Presse), indicateurs Professionnels/Historique/Aptitude (nécessitent des requêtes
d'agrégation sur les données déjà collectées), ou poursuite de l'extension de la
surface API (jockeys/entraineurs/résultats/cotes/statistiques, puis authentification
réelle).

## Conventions de développement

- Commits atomiques.
- Développement sur la branche develop.
- Documentation synchronisée avec le code.
- Aucune modification rétroactive des historiques.
- Respect des procédures TurfIA.

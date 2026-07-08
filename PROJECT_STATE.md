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
  (L032.1 §6), gestion d'erreurs centralisée y compris 401/403/404/409/422/429
  (L023 §4.1, L016 §7). Endpoints : `/system/health`, `/system/version` (publics),
  `POST /auth/login`, `POST /auth/logout`, `GET /hippodromes`,
  `POST/GET/PATCH/DELETE /reunions/{id}`, `POST/GET /reunions/{id}/courses`,
  `POST/GET/PATCH/DELETE /courses/{id}`, `POST/GET/PATCH/DELETE /chevaux/{id}`,
  `POST/GET/PATCH/DELETE /jockeys/{id}`, `POST/GET/PATCH/DELETE /entraineurs/{id}`,
  `POST/GET /courses/{id}/partants`, `GET/PATCH/DELETE /partants/{id}`,
  `POST/GET /courses/{id}/resultats`, `POST/GET /partants/{id}/cotes`,
  `POST/GET /courses/{id}/analyses`, `POST /courses/{id}/analyses/auto`,
  `GET /analyses/{id}` — le flux complet réunion → course →
  chevaux/jockeys/entraîneurs → partants → déclenchement d'analyse (manuel ou
  automatique depuis la collecte) → relecture est pilotable de bout en bout via
  HTTP, avec correction (PATCH) et suppression (DELETE) des ressources
  référentielles/métier. La création d'un partant vérifie l'existence de
  `cheval_id`, `jockey_id` et `entraineur_id` (404 ciblé, jamais une violation de
  contrainte SQL brute).
- **Authentification/RBAC réels** (cf. « Authentification » ci-dessous) : toutes
  les routes hors `/system/*` et `/auth/login` exigent un jeton de session valide ;
  chaque route impose un rôle minimal (L021 §4.1).
- **Collecte** (`src/collecte/`) : architecture multi-sources en 4 niveaux (données
  officielles, marché, consensus presse, base TurfIA propriétaire). Registre
  déclaratif de 12 sources (`src/collecte/registre.py`) avec statut vérifié par accès
  réseau réel (2026-07-07, complété pour la presse le 2026-07-07) :
  | Source | Niveau | Statut |
  | --- | --- | --- |
  | PMU | 1 (officiel) + 2 (marché) | **Implémentée** (`src/collecte/pmu/`) |
  | France Galop | 1 | Non implémentée — site atteignable (HTTP 301), structure non explorée |
  | LeTROT | 1 | Non implémentée — protection anti-bot (HTTP 403) |
  | ZEbet, Genybet, Unibet, Betclic | 2 | Non implémentées — non explorées |
  | Canalturf | 3 | **Implémentée** (`src/collecte/canalturf/`) — Quinté+ du jour uniquement, cf. ci-dessous |
  | Paris-Turf | 3 | Non implémentée — robots.txt bloque explicitement le user-agent `anthropic-ai` (`Disallow: /`), séparément de la règle générale `User-Agent: *` |
  | Geny | 3 | Non implémentée — protection anti-bot (HTTP 429) **et** robots.txt interdit les pages de pronostics/partants pour tous |
  | ZEturf | 3 | Non implémentée — robots.txt interdit `/partants/` pour tous |

  `CollecteService.collecter_programme_du_jour(jour)` : programme + participants PMU
  → référentiels (hippodrome/discipline/surface/état de piste/distance),
  réunion/course/partant, cheval/jockey/entraineur, cote directe, résultat si
  disponible — tout en get-or-create idempotent. Script manuel
  `scripts/collecter_programme.py --date DDMMYYYY`. Aucune tâche planifiée
  (L017/L033 hors périmètre).
- **Indicateurs réels** (`src/algorithms/indicateurs.py`) : sous-scores Marché
  (probabilité implicite du marché, marge neutralisée, normalisée sur le champ),
  Forme (moyenne normalisée des dernières positions, format « musique » PMU parsé et
  vérifié sur données réelles), Presse (rang dans le consensus multi-journaux
  Canalturf, cf. ci-dessous), Professionnels (moyenne des taux de victoires
  jockey/entraîneur/couple), Historique (taux de victoires du cheval à cet
  hippodrome, cf. L031.1 §5) et Aptitude (taux de victoires du cheval dans les mêmes
  distance/surface/état de piste) ; approximation partielle du risque par la taille
  du champ. `PreparationDonneesService.preparer_donnees_partants(course_id)`
  (`src/services/preparation_service.py`) construit ces indicateurs à partir des
  données déjà collectées et les met en forme pour `AnalyseService` — exclut les
  non-partants et les partants sans cote collectée plutôt que d'inventer une valeur.
  Professionnels/Historique/Aptitude s'appuient sur 5 requêtes d'agrégation SQL
  ajoutées à `CourseRepository` (`compter_performances_*`, victoires/courses en
  excluant la course en cours), transformées en score via
  `calculer_indicateur_reussite` (score neutre si l'échantillon a moins de 3
  courses). Professionnels est absente si ni jockey ni entraîneur ne sont connus ;
  Aptitude est absente si la course ne connaît pas ses distance/surface/état de
  piste ; Historique est toujours calculée (hippodrome toujours connu).
  Le sous-score Presse est best-effort : `ConsensusPresseService`
  (`src/services/consensus_presse_service.py`) est un collaborateur optionnel (défaut
  `None`) et toute indisponibilité de Canalturf (`ImportationError`) est journalisée
  puis ignorée plutôt que de faire échouer l'analyse. Exposé via `POST
  /courses/{id}/analyses/auto` et `scripts/analyser_course.py --course-id N` (ce
  dernier ne branche pas encore le service presse, cf. limites ci-dessous) : la
  boucle collecte → indicateurs → analyse est désormais complète et automatique,
  sans saisie manuelle.
- **Consensus presse** (`src/collecte/canalturf/`, `src/services/consensus_presse_service.py`) :
  scrape la page `courses_quinte.php` de Canalturf pour trouver le Quinté+ du jour,
  confirme via le `R{réunion}C{course}` extrait de la page que la course analysée
  est bien celle-là, puis extrait le classement du bloc « La sélection de la presse »
  (~14 titres de presse hippique agrégés par Canalturf lui-même). **Limité au
  Quinté+ du jour** (1 course/jour) : vérifié réellement que ce bloc n'existe sur
  aucune autre course de la page Canalturf.
- **Authentification** (`src/core/security.py`, `src/services/auth_service.py`,
  `api/routes/auth.py`, `api/dependencies/auth.py`) : jetons de session **opaques**
  côté serveur (pas de JWT) — L021 §3.3 décrit littéralement des « sessions »
  (durée limitée, expiration, invalidation à la déconnexion) ; un JWT
  auto-porteur ne peut satisfaire l'invalidation immédiate sans état côté serveur
  de toute façon, autant stocker directement une session opaque dans la nouvelle
  table `session` (jeton aléatoire `secrets.token_urlsafe`, seul son hash SHA-256
  est stocké, cf. L021 §5.1). Mots de passe bcrypt (L021 §3.2), vérification en
  temps constant même si le login est inconnu (pas d'énumération de comptes par
  timing). RBAC (L021 §4.1) via `exiger_roles(*roles)` sur chaque route : matrice
  LECTURE (tout rôle, GET) / DECLENCHEMENT_ANALYSE (Administrateur/Analyste/
  Automatisation, déclenchement d'analyse) / ECRITURE_DONNEES (Administrateur/
  Automatisation, POST/PATCH/DELETE). `POST /auth/login` limité en débit par
  (login, IP) — L021 §7.2.1. Connexion/échec de connexion/déconnexion journalisés
  dans `audit` (table déjà prévue au schéma, jusque-là inutilisée). Bootstrap des
  comptes via `scripts/creer_utilisateur.py` (mot de passe saisi de façon
  interactive, jamais en argument CLI) — l'API n'expose pas de route de création
  d'utilisateurs.
- **PATCH/DELETE** : PATCH partiel (`exclude_unset`) sur réunion/course/partant/
  cheval/jockey/entraineur ; pas de PUT (avec des FK obligatoires immuables et des
  champs presque tous optionnels, un remplacement complet n'apporte rien de plus
  qu'un PATCH). DELETE réel sur ces mêmes ressources : une violation de contrainte
  FK `ON DELETE RESTRICT` (déjà en place, cf. L011 §9) est traduite en 409 plutôt
  que vérifiée à l'avance (évite une fenêtre de concurrence). **Jamais** de PATCH/
  DELETE sur résultat/cote/analyse et dérivés (historisés, cf. L011 §15).
- **Tests** : 119 tests unitaires (algorithmes, configuration, mappers PMU/
  Canalturf, sécurité — hachage mot de passe/jeton, limiteur de débit, dépendances
  RBAC) + 69 tests d'intégration (API courses/analyses/résultats/cotes/PATCH/
  DELETE, AuthService, authentification API bout en bout, branchement presse et
  Professionnels/Historique/Aptitude — repositories/services en mémoire,
  `tests/integration/`), tous verts (188 au total).

## Correction notable apportée au SAD pendant l'implémentation

La table documentée `analyse` (L011 §8.3, L030.3 §3) est implémentée sous le nom
physique `analyses` : PostgreSQL réserve `ANALYSE` comme alias de la commande
`ANALYZE`, provoquant une erreur de syntaxe dès que l'identifiant est utilisé hors
position `CREATE TABLE`. Documenté dans les deux livrables concernés ; le nom
conceptuel et les colonnes `analyse_id` sont inchangés.

`src/collecte/` n'était pas anticipé dans L014 (arborescence) — ajouté avec une note
explicite dans L014 §6.1.1.

L031.2 §3 définit la famille « Historique » comme « performances TurfIA passées »,
sans détail. L031.1 §5 (tableau des familles, cohérent avec le code) précise
« Historique → Hippodrome » : interprété comme la performance passée du cheval à cet
hippodrome précis, pas comme une méta-mesure de la performance passée du moteur
TurfIA lui-même (qui relèverait du futur module Statistiques, L031.7, non
implémenté). Aptitude est bornée à distance/surface/état de piste (le facteur
hippodrome de L031.2 étant déjà couvert par Historique, pour éviter un double
comptage).

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
- Le sous-score Presse n'est calculé que pour la course Quinté+ du jour (1
  course/jour) : c'est la seule qui porte un véritable consensus multi-journaux sur
  Canalturf, vérifié réellement (les autres courses de la page Canalturf n'ont que
  des sélections mono-source, hors périmètre de la famille « Presse » telle que
  définie en L031.2/L031.3). Pour toute autre course, la clé `"presse"` est
  simplement absente du calcul (mécanisme déjà toléré par `calculer_score`).
- `scripts/analyser_course.py` ne branche pas encore `ConsensusPresseService` (il
  construit `PreparationDonneesService` sans ce collaborateur optionnel) —
  uniquement `POST /courses/{id}/analyses/auto` en bénéficie pour l'instant.
- `Course.quinte` (colonne existante en base) n'est pas encore alimentée par le
  collecteur PMU (`CollecteService`) — non nécessaire au fonctionnement du
  consensus presse actuel, qui s'appuie sur le `R{réunion}C{course}` extrait de
  Canalturf lui-même, pas sur cette colonne.

## Limites connues de l'authentification/RBAC (documentées, pas cachées)

- Limiteur de débit (`src/core/rate_limiter.py`) en mémoire, un seul processus —
  ne protège pas contre la force brute si l'API tourne sur plusieurs workers/
  instances sans état partagé (pas de Redis ou équivalent dans cette tranche).
- L'audit (table `audit`) n'enregistre que les événements d'authentification
  (connexion, échec, déconnexion) — pas encore chaque écriture sur chaque
  ressource (cf. « Prochaine étape »).
- Pas de purge des sessions expirées/révoquées dans la table `session` — elle
  grossit indéfiniment ; acceptable pour le volume actuel, à revoir si l'usage
  s'intensifie (même logique que les autres limites déjà actées : get-or-create
  non atomique, etc.).
- Pas de route de gestion des utilisateurs (création/désactivation) via l'API :
  uniquement `scripts/creer_utilisateur.py`, en ligne de commande.
- Un PATCH sur `course` référençant un `distance_id`/`surface_id`/`etat_piste_id`
  référentiel inconnu n'est pas validé avant l'écriture (contrairement à
  `jockey_id`/`entraineur_id` sur un partant) : remonte en violation de
  contrainte FK brute (500), pas en 404 ciblé.

## Explicitement hors périmètre (travail futur, non implémenté)

- Automatisations planifiées (L017/L033) — aucun scheduler, `automations/` est un
  squelette vide.
- Interface HTML (L018) — `html/` est un squelette vide.
- Endpoints résultats/cotes en écriture, PATCH/DELETE sur les ressources
  référentielles/métier et authentification/RBAC réels sont désormais
  implémentés (cf. ci-dessus). Reste hors périmètre : endpoints pour le module
  Statistiques (dépend du module lui-même, non construit), administration des
  utilisateurs via l'API.
- Module statistiques (L030.4, L031.7) — aucun code. La vraie définition L031.2 de
  « Historique » (performance passée du moteur TurfIA lui-même) en dépend et n'est
  donc pas implémentée ; seule l'interprétation L031.1 (hippodrome) l'est (cf.
  ci-dessus).
- Collecte de niveau 1/2 partiellement implémentée (PMU uniquement, cf. ci-dessus).
- Tous les sous-scores de `src/algorithms/score.py` sont désormais calculés
  automatiquement depuis les données collectées, à l'exception de Value et Contexte
  (non traités dans les tranches Indicateurs/Presse/Professionnels-Historique-
  Aptitude). Le risque de la course n'est approximé que par la taille du champ
  (`calculer_indicateur_risque_taille_champ`) ; les autres facteurs de risque
  documentés (volatilité du marché, désaccord presse, changement de terrain, cf.
  L031.3 §3) restent hors périmètre.
- Les requêtes `compter_performances_*` s'exécutent une par une par partant (jusqu'à
  5 requêtes SQL par partant) — proportionné au volume actuel (déclenchement manuel),
  non optimisé (pas de requête groupée/matérialisée) si le volume devait augmenter.
- CI/CD ; le `Dockerfile`/`docker-compose.yml` sont un socle minimal, non durcis pour
  la production (mots de passe par défaut, pas de secrets management réel).

## Prochaine étape

L'essentiel de la surface API et l'authentification/RBAC réelle sont désormais en
place. Pistes possibles : module Statistiques (L031.7 — débloquerait la vraie
définition L031.2 de « Historique » et les familles Value/Contexte, ainsi que des
endpoints de lecture pour ce module), audit systématique des écritures (au-delà
des seuls événements d'authentification), administration des utilisateurs via
l'API, exploration d'une deuxième source niveau 1 (France Galop) ou niveau 3
(pour sortir du Quinté+-only de Canalturf), interface HTML (L018).

## Conventions de développement

- Commits atomiques.
- Développement sur la branche develop.
- Documentation synchronisée avec le code.
- Aucune modification rétroactive des historiques.
- Respect des procédures TurfIA.

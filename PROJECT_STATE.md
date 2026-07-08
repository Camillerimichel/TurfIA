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
- **Module Statistiques** (cf. « Statistiques et ROI réel » ci-dessous) : ROI réel
  a posteriori (comparé au rapport officiel PMU) et 6 tables statistiques agrégées
  (L030.4), désormais alimentées — `PROJECT_STATE.md` documentait jusqu'ici
  l'absence totale de code pour ce module.
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
  | Zone-Turf | 3 | **Implémentée** (`src/collecte/zoneturf/`) — Quinté+ du jour uniquement, combinée à Canalturf, cf. ci-dessous. Source hors taxonomie initiale, ajoutée à la demande de l'utilisateur (compte créé sur le site, non nécessaire pour la page utilisée — publique) |
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
  vérifié sur données réelles), Presse (moyenne des rangs dans les consensus
  multi-journaux Canalturf et Zone-Turf combinés, cf. ci-dessous), Professionnels
  (moyenne des taux de victoires jockey/entraîneur/couple), Historique (taux de
  victoires du cheval à cet hippodrome, cf. L031.1 §5) et Aptitude (taux de
  victoires du cheval dans les mêmes distance/surface/état de piste) ;
  approximation partielle du risque par la taille
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
  `None`) et l'indisponibilité de chaque source (`ImportationError`) est journalisée
  et encaissée indépendamment — une source en panne n'empêche jamais l'autre de
  contribuer. Exposé via `POST /courses/{id}/analyses/auto` et
  `scripts/analyser_course.py --course-id N` (ce dernier ne branche pas encore le
  service presse, cf. limites ci-dessous) : la boucle collecte → indicateurs →
  analyse est désormais complète et automatique, sans saisie manuelle.
- **Consensus presse** (`src/collecte/canalturf/`, `src/collecte/zoneturf/`,
  `src/services/consensus_presse_service.py`) : combine deux sources, chacune
  vérifiée réellement comme ne portant un vrai consensus multi-titres que pour la
  course Quinté+ du jour (1 course/jour) :
  - **Canalturf** : scrape `courses_quinte.php` pour trouver le Quinté+, confirme
    via le `R{réunion}C{course}` de la page, extrait le bloc « La sélection de la
    presse » (~14 titres de presse hippique).
  - **Zone-Turf** : une seule page (`/quinte/`) porte à la fois le repère
    `R{réunion} C{course}` et le tableau « Les pronostics de la presse du Tiercé
    Quarté Quinté » ; seule la ligne « Synthèse Quinté de la presse » (consensus
    sur 7 titres) est utilisée — la sélection maison Zone-Turf (première ligne du
    tableau) est mono-source, hors périmètre, même principe que Canalturf.
  - Les deux sous-scores individuels (`calculer_indicateur_presse`) sont moyennés
    (`calculer_indicateur_presse_combine`) quand les deux sources répondent ;
    sinon la seule source disponible est utilisée seule ; si aucune ne répond, la
    clé `"presse"` est simplement absente.
  - Source Zone-Turf ajoutée hors de la taxonomie niveau 3 initiale (Paris-Turf/
    Geny/Canalturf/ZEturf) : découverte via un compte créé par l'utilisateur sur
    le site, mais la page utilisée est publique — le compte n'était pas
    nécessaire pour cette donnée précise.
  - **Décision explicite (2026-07-08) : l'espace abonnés du site (`/abonnes/`,
    historiques inclus) n'est pas automatisé**, même avec un compte valide.
    `robots.txt` l'interdit pour `User-agent: *` (tout crawler, pas seulement un
    bot précis — contrairement au blocage `anthropic-ai` de Paris-Turf), et
    l'automatiser exposerait le compte personnel de l'utilisateur aux CGU du
    site. Les indicateurs Historique/Aptitude/Professionnels restent alimentés
    uniquement par les données déjà collectées (PMU), qui s'enrichissent avec le
    temps plutôt que via cet historique tiers.
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
  Automatisation, POST/PATCH/DELETE) / ADMINISTRATION (Administrateur seul,
  consultation de l'audit, cf. ci-dessous). `POST /auth/login` limité en débit
  par (login, IP) — L021 §7.2.1. Bootstrap des comptes via
  `scripts/creer_utilisateur.py` (mot de passe saisi de façon interactive,
  jamais en argument CLI) — l'API n'expose pas de route de création
  d'utilisateurs.
- **Audit systématique des écritures (2026-07-08)** (`src/core/audit.py`,
  `src/repositories/audit_repository.py`, `api/routes/audit.py`) : en plus des
  événements d'authentification déjà journalisés (connexion, échec, déconnexion),
  chaque POST/PATCH/DELETE de `api/routes/courses.py` (réunion/course/cheval/
  jockey/entraineur/partant/résultat/cote) et chaque déclenchement d'analyse
  (`api/routes/analyses.py`) crée désormais une ligne dans `audit` — auteur,
  action (`{creation,modification,suppression}_{ressource}` ou
  `declenchement_analyse`), objet concerné, état avant/après sérialisé en JSON
  (`serialiser_etat`, `dataclasses.asdict` + `json.dumps`). L'écriture métier et
  son audit partagent la même transaction par requête (`src/database/
  connection.py::session`, commit unique en fin de requête) : un échec de
  l'insertion d'audit annule toute la transaction, y compris l'écriture — pas de
  gestion d'erreur spécifique nécessaire, l'échec remonte comme n'importe quel
  autre échec SQL (cf. `api/middlewares/error_handler.py`). `GET /audit`
  (RBAC `ADMINISTRATION`, `?limite=200` par défaut) permet de la consulter.
  Hors périmètre : les écritures des traitements planifiés (`ControleRoiService`,
  `StatistiqueService`, `CollecteService`, hors requête API authentifiée, sans
  utilisateur à attribuer) restent couvertes uniquement par la journalisation
  structurée (`src/core/logging.py`, cf. L022), pas par `audit`. La gestion des
  utilisateurs reste script-only, donc hors scope également.
- **Statistiques et ROI réel** (`src/algorithms/controle_roi.py`,
  `src/services/controle_roi_service.py`, `src/services/statistique_service.py`,
  `src/repositories/statistique_repository.py`, `scripts/calculer_statistiques.py`,
  `GET /statistiques/*`) : ferme la boucle collecte → analyse → résultat réel →
  statistiques.
  - **Découverte réelle (2026-07-08)** : PMU expose `GET /programme/{date}/
    R{n}/C{n}/rapports-definitifs` (jusque-là non exploité), qui donne le rapport
    officiel réel par type de pari une fois la course arrivée — permet de calculer
    un vrai ROI sans nouvelle source externe, juste une extension de l'adaptateur
    PMU déjà en place (`src/collecte/pmu/client.py`).
  - **Extension (2026-07-08) : 5 types de pari** (cf. L031.6 §5) —
    `AnalyseService.analyser_course` génère désormais Simple Gagnant, Simple
    Placé, Couplé Gagnant, Couplé Placé et 2 sur 4 par analyse (au lieu du seul
    Simple Gagnant), via `construire_paris` (`src/algorithms/classement.py`) à
    partir des catégories déjà assignées (Base élargie à `rang <= 2` pour
    permettre « Base n°1 + Base n°2 », cf. `categoriser`). Budget réparti entre
    les types réellement constructibles selon `REPARTITION_BUDGET_PAR_DEFAUT`
    (Simple Placé 35 %, 2 sur 4 25 %, Simple Gagnant 20 %, Couplé Placé 15 %,
    Couplé Gagnant 5 % — pondération choisie pour optimiser les gains fréquents
    plutôt que les gros gains rares, décision explicite de l'utilisateur) ; un
    type non constructible redistribue sa part aux autres. Quinté Flexi reste
    hors périmètre (structure de rapport multi-paliers + mise fractionnée
    disproportionnée par rapport aux 5 autres types).
  - **Vérifié réellement (2026-07-08)** contre une course Quinté+ déjà arrivée
    (R1C8, 07/07/2026) : Couplé Gagnant/Placé et 2 sur 4 ne sont exposés par PMU
    (`rapports-definitifs`) que sur les courses Quinté+ (une course ordinaire
    n'expose que `COUPLE_ORDRE`, à ordre exigé, un pari PMU différent) — un pari
    de ce type généré sur une course ordinaire ne trouvera donc jamais de
    rapport PMU correspondant, journalisé et ignoré par `ControleRoiService`
    plutôt que deviné.
  - `src/collecte/pmu/mappers.py` : `extraire_rapport_simple` (Simple
    Gagnant/Placé, un dividende par cheval gagnant), `extraire_rapport_couple`
    (Couplé Gagnant/Placé, `frozenset` de 2 numéros — ordre indifférent, à ne pas
    confondre avec `COUPLE_ORDRE`), `extraire_rapport_deux_sur_quatre` (2 sur 4,
    reconstruit les 4 premiers arrivés par union des paires PMU, teste
    « au moins 2 des 4 numéros joués en commun », pas une paire exacte) —
    `TYPES_PARI_PMU` fait la correspondance type_pari TurfIA -> code PMU.
    `src/algorithms/controle_roi.py` : `calculer_gains_simple/couple/
    deux_sur_quatre`, fonctions pures correspondantes.
  - `ControleRoiService.calculer_controles_manquants()` résout `pari.combinaison`
    (1 ou plusieurs `partant_id` internes séparés par `-`) vers les vrais
    numéros de course, compare au rapport PMU du type correspondant, persiste un
    contrôle agrégé (mise/gains sommés sur tous les paris de l'analyse) dans
    `controle_roi` (table déjà prévue au schéma, jusque-là inutilisée) —
    best-effort par pari (rapport pas encore disponible pour ce type précis, ou
    type de pari non pris en charge : journalisé, pari suivant poursuivi, jamais
    toute l'analyse abandonnée).
  - **Correction du bug de régression sur `statistique_pari` (2026-07-08)** :
    nouvelle table `controle_roi_pari` (migration
    `20260708_1600_ajout_controle_roi_pari.sql`, cf. `sql/schema/03_analyses.sql`)
    — une ligne par **pari** (mise/gains/valide), en plus de `controle_roi` qui
    reste l'agrégat par **analyse** (inchangé, toujours utilisé par
    statistique_globale/score/hippodrome/discipline). `ControleRoiService`
    persiste désormais les deux (`create_controle_roi_pari` en plus de
    `create_controle_roi`, cf. `src/repositories/analyse_repository.py`).
    `StatistiqueRepository.calculer_paris()` regroupe maintenant sur
    `controle_roi_pari JOIN pari`, sans jointure vers l'agrégat par analyse —
    vérifié réellement contre une instance PostgreSQL locale (2 paris de types
    différents dans la même analyse : mises/gains par type corrects et non
    dupliqués, alors que l'ancienne requête aurait donné 11,00 €/81,60 € pour
    les deux types au lieu de 10,00 €/14,00 € et 1,00 €/67,60 € respectivement).
  - `StatistiqueService.calculer_toutes()` agrège `controle_roi` en 6 tables
    (globale/score/hippodrome/discipline/pari/modèle, cf. L030.4) — toujours une
    nouvelle ligne, jamais une mise à jour (cf. L030.4 §10). Les tranches de score
    réutilisent `SEUILS_DECISION_PAR_DEFAUT` de `src/algorithms/score.py`.
  - Déclenchement uniquement via `scripts/calculer_statistiques.py` (pas de route
    API d'écriture, cohérent avec L017/L033 hors périmètre — aucun ordonnanceur).
    Lecture via `GET /statistiques/globale|scores|hippodromes|disciplines|paris|
    modeles` (RBAC `LECTURE`).
  - Vérifié contre une instance PostgreSQL locale réelle (3 courses, 2 contrôlées
    dont 1 gagnante/1 perdante, 1 analysée mais non jouée → agrégats corrects sur
    les 6 tables) et contre l'API PMU réelle (rapport Simple Gagnant d'une course
    déjà arrivée le jour même). L'extension à 5 types de pari a été rejouée en
    mémoire (pas PostgreSQL) contre les rapports réels capturés de R1C8
    (07/07/2026) : gains recalculés identiques aux dividendes PMU réels pour
    Simple Gagnant/Placé, Couplé Gagnant/Placé et 2 sur 4.
  - **Limites assumées** (cf. ci-dessous) : le remboursement réglementaire PMU
    pour un partant devenu non-partant après l'analyse n'est pas modélisé ;
    `statistique_modele` agrège les analyses déjà faites par version, ce n'est
    **pas** le moteur de rejeu/backtesting complet décrit en L031.7 §4 (comparer
    des versions du modèle sur un historique identique) — resterait à construire
    si un jour plusieurs jeux de pondérations coexistent.
- **PATCH/DELETE** : PATCH partiel (`exclude_unset`) sur réunion/course/partant/
  cheval/jockey/entraineur ; pas de PUT (avec des FK obligatoires immuables et des
  champs presque tous optionnels, un remplacement complet n'apporte rien de plus
  qu'un PATCH). DELETE réel sur ces mêmes ressources : une violation de contrainte
  FK `ON DELETE RESTRICT` (déjà en place, cf. L011 §9) est traduite en 409 plutôt
  que vérifiée à l'avance (évite une fenêtre de concurrence). **Jamais** de PATCH/
  DELETE sur résultat/cote/analyse et dérivés (historisés, cf. L011 §15).
- **Tests** : 168 tests unitaires (algorithmes dont ROI réel des 5 types de
  pari, configuration, mappers PMU/Canalturf/Zone-Turf, sécurité — hachage mot
  de passe/jeton, limiteur de débit, dépendances RBAC, sérialisation d'audit)
  + 93 tests d'intégration (API courses/analyses/résultats/cotes/PATCH/DELETE/
  statistiques/audit, AuthService, authentification API bout en bout,
  branchement presse combinée Canalturf+Zone-Turf, Professionnels/Historique/
  Aptitude, ControleRoiService (5 types de pari + détail par pari
  `controle_roi_pari`), StatistiqueService — repositories/services en mémoire,
  `tests/integration/`), tous verts (261 au total).

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

## Limites connues du module Statistiques (documentées, pas cachées)

- 5 types de pari sont contrôlés contre un rapport réel (Simple Gagnant/Placé,
  Couplé Gagnant/Placé, 2 sur 4, cf. ci-dessus) ; Quinté Flexi ou tout autre
  type rencontré est journalisé et ignoré, pas deviné. Couplé Gagnant/Placé et
  2 sur 4 ne sont réellement disponibles côté PMU que sur les courses Quinté+
  (vérifié le 2026-07-08) — un pari de ce type généré sur une course ordinaire
  ne trouve jamais de rapport correspondant, journalisé et ignoré.
- Le remboursement réglementaire PMU quand un partant joué devient non-partant
  après l'analyse n'est pas modélisé (règles pari-mutuel non triviales, non
  vérifiées) : traité simplement comme un pari perdant si son numéro/sa
  combinaison ne correspond à aucune combinaison gagnante.
- `statistique_pari` s'appuie sur `controle_roi_pari` (une ligne par pari, cf.
  ci-dessus) — corrigé le 2026-07-08, plus de double-comptage même quand une
  analyse produit plusieurs types de pari.
- `statistique_modele` est peuplée par simple agrégation des analyses déjà
  faites, groupées par `version` — ce n'est pas le moteur de rejeu/backtesting
  complet décrit en L031.7 §4 (recalculer tout un historique avec de nouveaux
  paramètres pour comparer des versions), qui reste à construire.
- Pas de purge/archivage des lignes historisées dans les 6 tables statistiques —
  chaque exécution de `scripts/calculer_statistiques.py` ajoute une nouvelle
  ligne par table (cf. L030.4 §10, volontaire), mais rien ne limite leur nombre
  dans le temps.

## Limites connues de l'authentification/RBAC (documentées, pas cachées)

- Limiteur de débit (`src/core/rate_limiter.py`) en mémoire, un seul processus —
  ne protège pas contre la force brute si l'API tourne sur plusieurs workers/
  instances sans état partagé (pas de Redis ou équivalent dans cette tranche).
- La table `audit` grossit indéfiniment (comme les tables statistiques, cf.
  ci-dessus) — aucune purge/archivage, `GET /audit` limite juste le nombre de
  lignes retournées par appel (`?limite`, défaut 200), sans pagination réelle
  (offset/curseur).
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
  référentielles/métier, authentification/RBAC réels et module Statistiques
  (ROI réel + 6 tables agrégées) sont désormais implémentés (cf. ci-dessus).
  Reste hors périmètre : administration des utilisateurs via l'API, moteur de
  rejeu/backtesting L031.7 §4 (cf. « Limites connues du module Statistiques »).
- La vraie définition L031.2 de « Historique » (performance passée du moteur
  TurfIA lui-même, pas du cheval) dépendrait de ce moteur de rejeu ; seule
  l'interprétation L031.1 (hippodrome) est implémentée (cf. ci-dessus).
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

L'essentiel de la surface API, l'authentification/RBAC réelle, une deuxième
source de consensus presse, le module Statistiques (ROI réel + 6 tables
agrégées, granularité par pari via `controle_roi_pari`), 5 types de pari
(Simple Gagnant/Placé, Couplé Gagnant/Placé, 2 sur 4) et l'audit systématique
des écritures (au-delà des seuls événements d'authentification) sont désormais
en place. Pistes possibles : moteur de rejeu/backtesting L031.7 §4 (comparer
des versions du modèle sur un historique identique — débloquerait aussi la
vraie définition L031.2 de « Historique » et les familles Value/Contexte),
Quinté Flexi, exploration d'une source niveau 1 (France Galop) pour sortir du
mono-source PMU, sortir du Quinté+-only pour la Presse, interface HTML (L018),
administration des utilisateurs via l'API.

## Conventions de développement

- Commits atomiques.
- Développement sur la branche develop.
- Documentation synchronisée avec le code.
- Aucune modification rétroactive des historiques.
- Respect des procédures TurfIA.

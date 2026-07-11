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
  | France Galop | 1 | Non implémentée — vérifiée réellement le 2026-07-08 : site atteignable, sans anti-bot, mais robots.txt n'autorise que des listes sommaires de réunions (`/fr/courses/aujourdhui` etc.) et interdit tout le détail exploitable (`/fr/courses/reunion/*`, `/fr/course/`, `/fr/cheval/`, `/fr/jockey/`, `/fr/entraineur/`) — strictement moins que PMU, aucun collecteur à construire |
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
  Professionnels/Aptitude s'appuient sur des requêtes d'agrégation SQL ajoutées à
  `CourseRepository` (`compter_performances_*`, victoires/courses en excluant la
  course en cours), transformées en score via `calculer_indicateur_reussite`
  (score neutre si l'échantillon a moins de 3 courses). Professionnels est
  absente si ni jockey ni entraîneur ne sont connus ; Aptitude est absente si
  la course ne connaît pas ses distance/surface/état de piste ; Historique est
  toujours calculée (hippodrome toujours connu) mais **rebranchée sur le vrai
  signal moteur depuis le 2026-07-09** (cf. « Rebranchement de la famille
  Historique » ci-dessous) — plus une performance de cheval.
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
  - **Extension (2026-07-08) : 6 types de pari** (cf. L031.6 §5) —
    `AnalyseService.analyser_course` génère désormais Simple Gagnant, Simple
    Placé, Couplé Gagnant, Couplé Placé, 2 sur 4 et Quinté Flexi par analyse (au
    lieu du seul Simple Gagnant), via `construire_paris` (`src/algorithms/
    classement.py`) à partir des catégories déjà assignées (Base élargie à
    `rang <= 2` pour permettre « Base n°1 + Base n°2 », cf. `categoriser`).
    Budget réparti entre les types réellement constructibles selon
    `REPARTITION_BUDGET_PAR_DEFAUT` (Simple Placé 30 %, 2 sur 4 25 %, Simple
    Gagnant 20 %, Couplé Placé 15 %, Couplé Gagnant 5 %, Quinté Flexi 5 % —
    pondération choisie pour optimiser les gains fréquents plutôt que les gros
    gains rares, décision explicite de l'utilisateur ; Quinté Flexi reçoit la
    plus petite part, variance la plus forte de tous) ; un type non
    constructible redistribue sa part aux autres.
  - **Quinté Flexi (2026-07-08)** : mécanique Flexi vérifiée réellement (champ
    `valeursFlexiAutorisees` des pools PMU, programme du jour) — jouer à
    100/50/25 % du prix plein (aucune valeur intermédiaire), et toucher la même
    fraction du dividende si gagnant. Sélection (L031.6 §5, littéral) : Bases +
    Chances régulières + Outsider principal + Tocard éventuel si son ROI propre
    reste positif (`_construire_selection_quinte`). Si la sélection dépasse 5
    chevaux, le Quinté+ joue automatiquement toutes les combinaisons de 5
    (C(n,5)) au tarif Flexi le plus élevé qui tient dans le budget alloué
    (`_calculer_mise_quinte_flexi` — 100 puis 50 puis 25 % ; si même 25 %
    dépasse le budget alloué, le pari est simplement omis, sa part de budget
    reste non engagée plutôt que redistribuée, cas rare). Contrôle réel : les
    C(n,5) sous-combinaisons sont recalculées à partir du nombre de chevaux
    résolus (pas de colonne dédiée, pas de migration), et chacune est comparée
    indépendamment à 3 paliers de gain (désordre exact, Bonus 4sur5, Bonus 3,
    cf. `extraire_rapport_quinte`, `calculer_gains_quinte_flexi`) — une même
    sélection peut gagner sur plusieurs sous-combinaisons à la fois. Vérifié :
    le Flexi n'est pas exclusif au Quinté+ (aussi présent sur 2 sur 4/Multi/
    Mini Multi/Pick5 dans le JSON réel, contrairement à une affirmation trouvée
    dans une source secondaire non fiable) — non exploité pour les 5 autres
    types dans cette tranche (hors périmètre, pas demandé).
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
    déjà arrivée le jour même). L'extension aux 6 types de pari a été rejouée en
    mémoire (pas PostgreSQL) contre les rapports réels capturés de R1C8
    (07/07/2026) : gains recalculés identiques aux dividendes PMU réels pour
    Simple Gagnant/Placé, Couplé Gagnant/Placé, 2 sur 4 et Quinté Flexi (y
    compris un champ de 6 chevaux, 1 désordre exact + 5 Bonus 4sur5 simultanés).
  - **Limite assumée** : le remboursement réglementaire PMU pour un partant
    devenu non-partant après l'analyse n'est pas modélisé.
- **Moteur de rejeu/backtesting (2026-07-09)** (`src/algorithms/rejeu.py`,
  `scripts/rejouer_versions.py`, L031.7 §4-5) : compare les 7 indicateurs
  L031.7 §5 (ROI global, ROI par tranche de score/hippodrome/type de pari,
  taux de réussite, drawdown, stabilité) de plusieurs jeux de
  `poids_score`/`poids_risque` sur un même historique de courses réelles déjà
  arrivées, à budget constant.
  - **Indicateurs étendus (2026-07-09)** : au départ seuls ROI global et taux
    de réussite étaient calculés ; les 5 autres ont été ajoutés dans un second
    temps, avant de construire l'interface HTML locale, pour que sa future
    page de comparaison de versions parte d'un `statistique_modele` déjà
    riche. ROI par tranche de score/hippodrome : agrégés au niveau de la
    **course** rejouée (mise/gains sommés sur tous ses paris, comme
    `controle_roi` pour l'agrégat par analyse) — le score de confiance et
    l'hippodrome sont des attributs de la course, pas du pari. ROI par type de
    pari : agrégé au niveau du **pari** individuel (comme `controle_roi_pari`).
    Drawdown (perte maximale en euros absolus entre un sommet et un creux sur
    la courbe de profit cumulé, dans l'ordre chronologique) et stabilité
    (écart-type population du ROI par course) : formules assumées, L031.7 §5
    ne les précise pas. Réutilise directement les dataclasses déjà existantes
    `StatistiqueScore`/`StatistiqueHippodrome`/`StatistiquePari` comme forme en
    mémoire des 3 répartitions, sérialisées en JSON (`roi_par_score`,
    `roi_par_hippodrome`, `roi_par_type_pari`, colonnes `TEXT` nullable) —
    réutilisable tel quel côté HTML plus tard, cohérent avec ce que les 3
    tables statistiques principales exposent déjà. `drawdown`/`stabilite` :
    colonnes `DECIMAL(8,2)` simples. **Point de vigilance découvert en
    testant réellement** : `calculer_score_final` n'écrête pas le bonus value
    bet, un score de confiance peut donc dépasser 100 (constaté : 102.5 sur
    une course de test) — une telle course est omise de `roi_par_score`,
    exactement comme `StatistiqueRepository.calculer_scores()` l'aurait déjà
    fait (même limite pré-existante, pas une régression introduite ici).
    `calculer_modeles()` (agrégation automatique existante, sans rapport avec
    le rejeu) n'est pas étendue : ces 5 colonnes restent `NULL` pour ses
    lignes, elle n'a pas la granularité par course/pari nécessaire.
  - **Découverte réelle en explorant le SAD** : `analyses.version` (cf. L030.3)
    n'est **pas** une version de modèle — c'est le statut Pré/Finale d'une même
    exécution. `StatistiqueRepository.calculer_modeles()` (agrégation
    existante) groupait déjà par cette colonne, un flou pré-existant
    indépendant de ce chantier, désormais documenté dans son docstring plutôt
    que laissé implicite. Le rejeu utilise sa propre notion de
    `version_modele` (chaîne libre décrivant le jeu de poids testé), sans lien
    avec `analyses.version` — les deux alimentent `statistique_modele` avec des
    sémantiques différentes.
  - **Persistance légère (décision de conception explicite)** : le rejeu
    recalcule tout en mémoire (`AnalyseService.analyser_course(...,
    persister=False)`, corrigé pour construire les paris même sans les
    persister — jusque-là mort dans ce mode) et ne persiste **qu'une** ligne de
    synthèse par version testée dans `statistique_modele` (`version_modele`
    élargi à `VARCHAR(60)`, nouvelle colonne `parametres` JSON pour la
    traçabilité L031.7 §7/§9) — aucune ligne dans `analyses`/`pari`/
    `controle_roi`. Comparer des versions = exécuter le script plusieurs fois
    puis lire `GET /statistiques/modeles`.
  - `ControleRoiService._calculer_gains_pari` rendue publique
    (`calculer_gains_pari`) et réutilisée telle quelle par le script — aucune
    duplication du dispatch par type de pari déjà testé.
  - Nouvelle méthode `CourseRepository.list_courses_avec_resultat(date_debut,
    date_fin)` (courses déjà arrivées, résultat connu) — périmètre du rejeu.
  - **Limites explicites** : le consensus Presse n'est pas rejouable
    (`ConsensusPresseService` scrape Canalturf/Zone-Turf en direct, uniquement
    le Quinté+ du jour même) — non branché dans le rejeu, comme dans
    `scripts/analyser_course.py`. Les familles Value/Contexte ne sont jamais
    produites (limite déjà existante, héritée telle quelle). Les seuils de
    décision (`determiner_decision`) ne sont pas paramétrables dans
    `AnalyseService`, seuls les poids le sont — non rejouables. La validation
    hors-échantillon (L031.7 §6.1) n'est pas automatisée : le script prend une
    fenêtre de dates en paramètre, à l'opérateur de choisir une fenêtre
    distincte de celle utilisée pour calibrer les poids testés. La décision
    finale (adopter/rejeter une version) reste une lecture humaine des
    résultats, jamais automatisée.
  - **Vérifié réellement (2026-07-09)** contre PostgreSQL local, à deux
    reprises : d'abord ROI global/taux de réussite (migration `version_modele`
    élargi + `parametres`, deux jeux de poids sur R1C8 du 07/07/2026 — deux
    lignes distinctes persistées, ROI identique entre les deux runs dans ce
    cas précis : artefact attendu du jeu de données synthétique n'exposant
    qu'une seule famille de sous-score, pas un bug, cf. `calculer_score`, une
    moyenne pondérée à un seul terme est invariante au poids utilisé) ; puis
    les 5 indicateurs supplémentaires (migration des 5 nouvelles colonnes,
    rejeu de la même course — `roi_par_hippodrome`/`roi_par_type_pari`/
    `drawdown`/`stabilite` correctement peuplés, `roi_par_score` vide comme
    attendu : score de confiance à 102.5 sur cette course de test, hors plage
    0-100, cf. ci-dessus).
- **PATCH/DELETE** : PATCH partiel (`exclude_unset`) sur réunion/course/partant/
  cheval/jockey/entraineur ; pas de PUT (avec des FK obligatoires immuables et des
  champs presque tous optionnels, un remplacement complet n'apporte rien de plus
  qu'un PATCH). DELETE réel sur ces mêmes ressources : une violation de contrainte
  FK `ON DELETE RESTRICT` (déjà en place, cf. L011 §9) est traduite en 409 plutôt
  que vérifiée à l'avance (évite une fenêtre de concurrence). **Jamais** de PATCH/
  DELETE sur résultat/cote/analyse et dérivés (historisés, cf. L011 §15).
- **Interface HTML locale (2026-07-09)** (`html/`, L018) — périmètre complet :
  Accueil + Courses/Analyses + Statistiques + **Historique (§8) et
  Administration (§10, périmètre complet incluant sauvegardes/supervision)**.
  - **Architecture délibérément minimale** (cf. L018 §2.2/§3.3, décision
    validée avec l'utilisateur) : aucune nouvelle dépendance — pas de Jinja2
    (pas de rendu serveur), pas de framework JS, pas de build step.
    `html/templates/*.html` sont des pages statiques pures ; tout le contenu
    dynamique vient du JS via `fetch()` (`html/static/js/api.js` centralise
    l'appel API, l'en-tête `Authorization: Bearer`, le parsing de l'enveloppe
    `{success, data}`/`{success:false, error}`, et la redirection vers
    `login.html` sur 401). **Indicateur de chargement global ajouté
    (2026-07-10)** : `apiFetch` incrémente/décrémente un compteur de requêtes
    en vol (bloc `try/finally`, donc retiré même en cas d'erreur) et
    affiche/masque une bannière injectée dynamiquement
    (`#indicateur-chargement-global`) — un seul point de câblage couvre
    tous les appels de toutes les pages, aucune page n'a eu besoin d'être
    modifiée individuellement. **Durée d'affichage minimale (300 ms)
    ajoutée** après un premier test manuel où la bannière n'apparaissait
    jamais : en local une requête peut se terminer en quelques millisecondes,
    affichage et retrait pouvant survenir dans le même cycle de rendu du
    navigateur (jamais peint du tout, pas juste trop rapide pour être vu).
    **`StaticFiles` remplacé par `StaticFilesSansCache`** (`Cache-Control:
    no-cache` sur chaque réponse statique) : un test manuel a montré le
    navigateur servir une version JS périmée après modification — force
    désormais la revalidation (ETag/Last-Modified déjà gérés nativement par
    Starlette) à chaque chargement plutôt qu'une politique heuristique.
    Navigation par query string
    (`course.html?id=42`), pas de routeur JS. Jeton stocké en `localStorage`
    (pas de cookies -> pas de CSRF à protéger, L018 §15 satisfait par
    construction). `api/main.py` monte `StaticFiles` (déjà fourni par
    Starlette/FastAPI, aucune dépendance ajoutée) sur `/static` et `/` (après
    tous les routeurs API, pour que `/api/v1/*` reste prioritaire).
  - **Gap réel trouvé en explorant l'API existante** : aucune route ne
    listait les réunions par date (seulement par id connu) — impossible de
    construire « réunions du jour ». Ajout de
    `CourseRepository.list_reunions_by_date(jour)` +
    `GET /reunions?date=YYYY-MM-DD` (défaut : aujourd'hui).
  - **N+1 corrigé (2026-07-09)** : `GET /courses/{id}/partants` fait
    désormais une seule jointure (`CourseRepository.
    list_partants_detail_by_course`, nouveau modèle `PartantDetail`) — noms
    cheval/jockey/entraîneur et dernière cote inclus directement dans
    `PartantOut`, plus d'appel `GET /chevaux/{id}`/`/jockeys/{id}`/
    `/entraineurs/{id}`/`/partants/{id}/cotes` par partant côté
    `course.js`. `PreparationDonneesService`/`list_partants_by_course`
    (utilisé pour le scoring) sont inchangés — la jointure ne concerne que
    la lecture HTML. Pas de pagination réelle non plus (même logique que
    `GET /audit`).
  - Déclenchement d'analyse (`POST /courses/{id}/analyses/auto`) derrière une
    confirmation JS explicite (`window.confirm`, cf. L018 §10.1 — action qui
    engage un budget).
  - Page Statistiques : les 6 tables déjà exposées, y compris `modeles` avec
    les indicateurs L031.7 §5 enrichis (`roi_par_score`/`roi_par_hippodrome`/
    `roi_par_type_pari` en JSON, dépliés dans un `<details>` par version).
  - **Vérifié réellement** : suite de tests complète (aucune régression),
    serveur de développement démarré, toutes les pages/assets confirmés en
    200 via `curl`, et un parcours authentifié complet (création d'un compte
    de vérification, login réel, appel `GET /reunions` et
    `GET /statistiques/modeles` avec le jeton obtenu) — compte de
    vérification nettoyé ensuite. **Limite honnête** : pas de navigateur ni
    d'outil d'automatisation de navigateur dans cet environnement — le JS
    lui-même (rendu, clics, formulaires) n'a pas été exécuté ni validé
    interactivement, seule la structure serveur/réseau l'a été.
  - **Historique (L018 §8, 2026-07-09)** : route transversale dédiée
    `GET /historique` (filtres date/hippodrome/type_pari/decision), une ligne
    = un pari (+ analyse et contrôle ROI par pari associés, LEFT JOIN) —
    granularité assumée, le détail complet (classement par partant) reste
    sur `course.html`. Nouveau `HistoriqueRepository`, page + JS dédiés.
  - **Administration (L018 §10, 2026-07-09, périmètre complet)** —
    l'utilisateur a choisi le périmètre complet (pas la version réduite
    envisagée initialement) :
    - *Journaux* : `journal` était créée en SQL mais jamais peuplée
      (`src/core/logging.py` n'écrivait que sur stdout). Nouveau
      `DbLogHandler` (`src/core/log_db_handler.py`) — connexion `psycopg`
      dédiée/courte par évènement, seuil `WARNING`+ seulement (borne volume),
      ignore les logs `psycopg.*` (anti-réentrance), n'appelle jamais
      `logging.*` en cas d'échec. Câblé dans `api/main.py`, désactivable via
      `LOG_JOURNAL_DB_ACTIF=false` (mis à `false` en test).
      `GET /administration/journaux`. **Vérifié réellement** : un vrai
      partant sans cote a déclenché un `logger.warning`, visible ensuite via
      la route.
    - *Lancer une automatisation* : réutilise les services déjà appelés par
      les scripts CLI (jamais de logique dupliquée, cf. L033 ADR-002).
      Nouveau `AutomatisationService.analyser_courses_du_jour` (seule
      orchestration réellement nouvelle — aucun script n'existait pour
      analyser plus d'une course à la fois) ; `collecte`/`statistiques`
      délèguent directement à `CollecteService`/`ControleRoiService`/
      `StatistiqueService`. Chaque déclenchement tracé dans `tache` (nouveau
      `TacheRepository`, table existante mais jamais peuplée jusqu'ici).
      3 routes `POST /administration/automatisations/*`, RBAC
      `ADMINISTRATION` (plus restrictif que `DECLENCHEMENT_ANALYSE` — choix
      documenté, sans conséquence pratique avec un seul compte Administrateur).
      **Affichage du résultat amélioré (2026-07-10)** : le premier test manuel
      réel a montré un JSON brut peu lisible — `administration.js` construit
      désormais un résumé structuré (compteurs, tableau des tables
      recalculées, liste des erreurs) au lieu de `JSON.stringify` ; les
      colonnes date/heure (`debut`, `fin`, `date_publication`,
      `date_evenement`) sont affichées en `DD/MM/AAAA - HH:MM` plutôt qu'en
      ISO brut.
      **Bug réel trouvé et corrigé (2026-07-10)** : `TacheRepository.
      terminer()` calculait `duree_ms` avec `now()`, qui renvoie la même
      valeur du début à la fin d'une transaction PostgreSQL (= `CURRENT_
      TIMESTAMP`, figé) — `demarrer()`/`terminer()` s'exécutant dans la même
      transaction (une connexion par requête), `duree_ms` valait toujours 0
      quel que soit le travail réel effectué entre les deux appels (constaté
      en test manuel : une vraie collecte de 55 courses affichait 0 ms).
      Remplacé par `clock_timestamp()` (heure réelle de chaque instruction,
      y compris au sein d'une même transaction) pour `debut`/`fin`/
      `duree_ms`. Vérifié réellement (`pg_sleep` dans une transaction de
      test annulée ensuite : 593 ms mesurés correctement).
      **Bug réel trouvé et corrigé (2026-07-10) : un second déclenchement
      d'« Analyser les courses du jour » faisait planter toute la route
      (500)** dès la première course déjà analysée dans cette version —
      `AnalyseRepository.create_analyse` levait un `psycopg.errors.
      UniqueViolation` (contrainte `uk_analyse_version`) jamais rattrapé, qui
      abortait toute la transaction PostgreSQL (donc toutes les courses
      suivantes du lot, pas seulement celle en conflit). Corrigé par un
      `SAVEPOINT` (`conn.transaction()`) autour de l'insertion, qui traduit
      la violation en `BusinessRuleError` sans invalider la transaction
      englobante ; `AutomatisationService.analyser_courses_du_jour` capture
      désormais `BusinessRuleError` en plus de `ValidationError` par course
      (isolation réelle, pas seulement pour les échecs de validation).
      Vérifié réellement (savepoint testé isolément contre PostgreSQL local,
      puis lot complet de 55 courses déjà analysées : 0 succès/55 « déjà
      analysée » au lieu d'un 500).
      **Bug de performance réel trouvé et corrigé (2026-07-10) :
      `ConsensusPresseService` refaisait les 2 requêtes réseau vers
      Canalturf/Zone-Turf pour CHAQUE course du lot**, alors que la page du
      Quinté+ du jour est strictement identique quel que soit le nombre de
      courses traitées — ~10 s/course (délai de politesse), soit plus de
      9 minutes pour 55 courses (constaté en test manuel : la route semblait
      « plantée »/sans réponse). Le Quinté+ du jour (page + classement) est
      désormais résolu au plus une fois par instance de service (cache
      mémoire), réutilisé pour toutes les courses suivantes du même lot.
      Vérifié réellement (lot complet de 55 courses : 2,7 s au lieu de
      plusieurs minutes) ; nouveau test dédié vérifiant que les clients
      Canalturf/Zone-Turf ne sont interrogés qu'une seule fois sur 5 courses
      consultées.
    - *Vérifier les sauvegardes* : `scripts/sauvegarder_base.py` (nouveau) —
      `pg_dump --format=custom` vers `data/sauvegardes/`, mot de passe transmis
      via `PGPASSWORD` (jamais en argument de ligne de commande, cf. L021
      §5.1). Suivi dans `tache` (`categorie='sauvegarde'`), pas de nouvelle
      table. `POST`/`GET /administration/sauvegardes` (déclenchement
      synchrone — limite documentée, pas de file d'attente). **Bug réel
      trouvé et corrigé en vérification** : `pg_dump` verrouille TOUTES les
      tables du schéma, y compris `migration` — or seul `turfia_migration`
      y avait SELECT (`turfia_app` utilisé par l'API n'avait rien), donc la
      première sauvegarde réelle a échoué avec « permission denied for
      table migration ». Corrigé par une nouvelle migration
      (`20260709_2000_grant_migration_table.sql`, GRANT SELECT seul, jamais
      INSERT/UPDATE) ; **vérifié réellement** ensuite (dump de 116 Ko,
      restaurabilité confirmée via `pg_restore -l`).
    - *Consulter les versions* : `scripts/publier_version.py` (nouveau, geste
      de déploiement comme `creer_utilisateur.py` — pas de route d'écriture),
      lit `git rev-parse HEAD`/branche, peuple `version` (créée en SQL,
      jamais peuplée jusqu'ici). `GET /administration/versions`. **Gap réel
      trouvé et corrigé** : la table `version` avait été oubliée du GRANT
      initial (`sql/schema/06_grants.sql`) — `turfia_app` n'avait aucun
      accès, 500 réel sur la première requête ; corrigé par
      `20260709_1900_grant_version_turfia_app.sql`. **Vérifié réellement**
      (publication réussie, commit/branche corrects en retour API).
    - *Gérer les paramètres* : nouveau `ParametreRepository`
      (`GET`/`PATCH /administration/parametres/{cle}`, catalogue fixe, pas de
      `POST`/`DELETE`). `AnalyseService` (via `get_analyse_service`) lit
      désormais ses poids depuis `parametre` (`poids_score.*`/
      `poids_risque.*`, 15 clés semées par migration à `1.0` = comportement
      inchangé) plutôt que la constante codée en dur — le fallback déjà
      existant (`poids or PONDERATIONS_PAR_DEFAUT`) protège contre toute
      régression si une clé est absente. `scripts/analyser_course.py`
      (instanciation directe hors FastAPI) reste sur les poids par défaut du
      code — asymétrie documentée, même limite déjà notée pour
      `ConsensusPresseService`. **Vérifié réellement** : PATCH réel d'une
      pondération puis retour à `1.0`.
    - *Contrôler la supervision* : périmètre volontairement réduit par
      rapport à L035 (pas de `psutil`, pas de métriques CPU/RAM/alertes) —
      connexion DB (ok/latence réelle), espace disque (`shutil.disk_usage`),
      échecs `tache` récents (24h), uptime process.
      `GET /administration/supervision`. **Vérifié réellement** contre
      PostgreSQL local (latence ~9 ms, ~96 Go disponibles).
- **Tests** : 215 tests unitaires (dont `AutomatisationService`,
  `DbLogHandler` — anti-réentrance/absence de crash sur DB indisponible,
  `SupervisionService`) + 143 tests d'intégration (dont Historique — filtres
  date/hippodrome/type de pari/décision —, Administration — RBAC,
  journaux, les 3 automatisations, sauvegarde réussie/échouée, versions,
  paramètres, supervision —, `CollecteService` (dont détection `Course.quinte`
  via `parisEvenement`), `ConsensusPresseService` (dont non-répétition des
  appels réseau par lot) et la suite de non-régression par déterminisme, cf.
  ci-dessous) — repositories/services en mémoire, `tests/integration/`), tous
  verts (358 au total).
- **Couverture de tests mesurée (2026-07-09, `pytest-cov`, cf. L020 §14.1
  cible ≥80 % sur `algorithms`/`services`)** : 90 % sur `src/algorithms`+
  `src/services` (81 % avant cette mesure). Deux vrais trous de couverture
  trouvés et fermés — `CollecteService` (30 % -> 100 %) et
  `ConsensusPresseService` (29 % -> 100 %) n'avaient jusqu'ici **aucun**
  test dédié malgré des fixtures déjà présentes pour cela
  (`tests/fixtures/pmu_programme_echantillon.json`/
  `pmu_participants_echantillon.json`, `FakePMUClient`, fixtures HTML
  Canalturf/Zone-Turf déjà utilisées pour tester les mappers). Nouveaux
  `tests/integration/test_collecte_service.py` (import réunion/course/
  partants sur échantillon PMU réel, réutilisation idempotente de
  l'hippodrome entre réunions, isolation d'une course/réunion en échec sans
  interrompre les suivantes — cf. L023 §5.2, unité de distance PMU inconnue)
  et `test_consensus_presse_service.py` (combinaison des deux sources,
  confirmation indépendante de la course Quinté+ du jour, isolation d'une
  source en panne — HTML minimal pour le scénario où les deux sources
  doivent confirmer la même course, sinon fixtures réelles déjà capturées).
  Nécessite d'étendre `FakeReferentielRepository`/`FakeCourseRepository`
  avec les méthodes `get_or_create_*` (absentes jusqu'ici, jamais utilisées
  par les tests API existants) et `FakePMUClient` avec
  `recuperer_programme`/`recuperer_participants`. `pytest-cov` ajouté à
  `requirements.txt` et à la CI (`--cov=src/algorithms --cov=src/services
  --cov-report=term-missing`, rapport seul, pas de seuil bloquant — cf.
  L020 §14.1 « une couverture élevée n'est pas une fin en soi »).
- **Suite de non-régression par déterminisme (2026-07-09, L020 §8.3)** :
  n'existait pas du tout jusqu'ici. Nouveau
  `tests/integration/test_non_regression_determinisme.py` — rejoue un
  scénario figé (3 partants, sans jockey/entraineur/consensus presse/
  conditions de piste connues, pondérations par défaut, `persister=False`)
  à travers `PreparationDonneesService` + `AnalyseService` et compare le
  résultat à une référence gelée
  (`tests/fixtures/reference_analyse_non_regression.json` : score de
  confiance, risque, ROI théorique, décision, budget, classement/catégorie/
  value bet par partant, paris générés). **Vérifié réellement que le test
  détecte un vrai écart** : altération manuelle de la référence (échec
  attendu) puis d'une pondération réelle (`marche` 1.0 -> 2.0, échec détecté
  avec le bon écart chiffré) avant restauration. Tout écart futur doit être
  expliqué et validé explicitement avant de régénérer la référence (cf.
  L009 §5.1), jamais un ajustement silencieux.

## Correction notable apportée au SAD pendant l'implémentation

La table documentée `analyse` (L011 §8.3, L030.3 §3) est implémentée sous le nom
physique `analyses` : PostgreSQL réserve `ANALYSE` comme alias de la commande
`ANALYZE`, provoquant une erreur de syntaxe dès que l'identifiant est utilisé hors
position `CREATE TABLE`. Documenté dans les deux livrables concernés ; le nom
conceptuel et les colonnes `analyse_id` sont inchangés.

`src/collecte/` n'était pas anticipé dans L014 (arborescence) — ajouté avec une note
explicite dans L014 §6.1.1.

**Rebranchement de la famille Historique (2026-07-09)** : le SAD est
contradictoire — L031.2 §3 définit « Historique » comme « performances TurfIA
passées », sans formule (recherche réelle : L031.2 §5 ne détaille que 5
familles sur 8, Historique/Value/Contexte n'ont aucune sous-section) ; L031.1
§5 (tableau des familles) dit « Historique → Hippodrome », interprété jusqu'ici
comme la performance du **cheval** à cet hippodrome. Décision actée avec
l'utilisateur : **remplacer** cette interprétation par le vrai signal moteur
(la lettre de L031.2), désormais que le moteur de rejeu/statistiques (L031.7
§4) est implémenté. `calculer_indicateur_historique_moteur`
(`src/algorithms/indicateurs.py`) lit le ROI réel du moteur à l'hippodrome de
la course via `StatistiqueRepository.get_dernier_hippodrome` (dernière ligne
de `statistique_hippodrome`, alimentée par les vrais `controle_roi` via
`scripts/calculer_statistiques.py`) : ROI normalisé sur `[-30 %, +30 %]`
(bornes assumées, clampées au-delà — aucune formule SAD pour ces bornes) si
aucune statistique ou échantillon `< 3` courses, la famille est **exclue** de
la moyenne pondérée plutôt que comptée à un score neutre (revu le
2026-07-10, cf. « Diagnostic demandé par l'utilisateur » plus bas et L031.2
§6.1 — la version neutre-à-plein-poids initiale s'est révélée être un vrai
bug de dilution du score, pas un choix à conserver).
`PreparationDonneesService` prend désormais un `StatistiqueRepository` requis
(pas optionnel : préserve l'invariant « Historique toujours calculée »).
`CourseRepository.compter_performances_cheval_hippodrome` (performance du
cheval à l'hippodrome) a été **supprimée** (plus aucun appelant) — cette
information n'est plus calculée nulle part après ce changement, elle n'était
pas exposée telle quelle par l'API/HTML. **Limite héritée pour le rejeu**
(`scripts/rejouer_versions.py`) : le signal lu pendant un rejeu reflète l'état
*actuel* de `statistique_hippodrome`, pas un instantané au moment de la course
rejouée — même limite déjà assumée pour Marché/Presse/Professionnels dans ce
moteur, pas une régression nouvelle. Aptitude reste bornée à distance/
surface/état de piste (le facteur hippodrome étant désormais couvert par
Historique-moteur, pas par le cheval, mais toujours pour éviter un double
comptage). Value et Contexte restent hors périmètre (aucune formule SAD non
plus, cf. ci-dessous).

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
- **Corrigé (2026-07-09)** : `scripts/analyser_course.py` branche désormais
  `ConsensusPresseService` (`CanalturfClient`/`ZoneTurfClient`, même câblage
  que `api/dependencies/services.py::get_preparation_service`) — auparavant
  seul `POST /courses/{id}/analyses/auto` en bénéficiait, le script CLI
  passait toujours à côté du sous-score Presse, y compris le jour du
  Quinté+. Vérifié réellement (course synthétique, script exécuté pour de
  vrai contre PostgreSQL local, aucune régression).
- **Corrigé (2026-07-10)** : `Course.quinte` (colonne existante en base) n'était
  jamais alimentée par le collecteur PMU — sans impact sur le consensus presse
  (qui s'appuie sur le `R{réunion}C{course}` extrait de Canalturf lui-même),
  mais un vrai bug visible côté HTML (`course.html` affiche « Quinté+ » à
  partir de ce champ) : toute course, y compris le vrai Quinté+ du jour,
  affichait « Non ». Le programme PMU signale le Quinté+ au niveau réunion
  (`parisEvenement`, `codePari` `QUINTE_PLUS`/`E_QUINTE_PLUS`, avec le
  `numOrdre` de la course visée), pas sur la course elle-même —
  `CollecteService.collecter_programme_du_jour` calcule maintenant l'ensemble
  des `numOrdre` visés par réunion et le transmet à
  `_importer_course_et_partants`. Trouvé en préparant les tests manuels de
  l'interface HTML (données de collecte réelles nettoyées avant relance avec
  le correctif).
- **Corrigé (2026-07-10)** : `DISCIPLINES_PMU` (`src/collecte/pmu/mappers.py`)
  ne connaissait que `HAIES`/`STEEPLE-CHASE` — une vraie collecte réelle du
  2026-07-10 a rencontré `HAIE`/`STEEPLECHASE` (sans le S/le tiret) sur une
  autre réunion, faisant échouer 8 courses (`Code discipline PMU inconnu`).
  PMU n'est pas cohérent sur l'orthographe exacte du code selon les réunions ;
  les deux variantes sont désormais acceptées (mappées vers les mêmes
  libellés `Haies`/`Steeple`), complété au fur et à mesure comme documenté.
- **Corrigé (2026-07-11)** : `SURFACES_PMU` ne connaissait que `HERBE` — une
  vraie collecte réelle du 2026-07-11 a rencontré `GAZON` sur une réunion
  internationale (R8, hippodrome américain, ex. Belmont), faisant échouer 5
  courses (`Code surface PMU inconnu`). `GAZON` mappé vers le même libellé
  `Gazon` que `HERBE`. **Anomalie PMU restant non résolue, documentée sans
  contournement** : ces 5 courses portent dans leur nom `(DIRT)` (piste en
  terre, pas en herbe), mais PMU leur attribue tout de même le code surface
  `GAZON` — la table `surface` locale n'a aucune entrée « Dirt »/« Terre »
  (seulement Gazon/PSF/Cendrée/Sable fibré, cf. seed L030.1), et rien
  n'indique que PMU distingue réellement Dirt du Gazon pour les réunions
  internationales dans ce champ. Corriger cela nécessiterait de deviner la
  surface depuis le texte libre du nom de course plutôt que depuis un champ
  structuré (contraire à L009 §2.1, « ne fais aucune hypothèse ») — laissé
  tel quel, l'indicateur Aptitude (surface) sera donc incorrect pour ces
  courses précises tant que PMU ne fournit pas un code distinct. Programme du
  11/07/2026 recollecté après correctif (transaction réelle, pas annulée) :
  les 5 courses R8C1/C2/C3/C6/C9 sont désormais importées.
- **`DIRT`/`SABLE` ajoutés à `SURFACES_PMU` à la demande explicite de
  l'utilisateur (2026-07-11)**, mappés vers de nouveaux libellés `Dirt`/
  `Sable` (créés automatiquement en base au premier usage via
  `ReferentielRepository.get_or_create_surface`, comme toute nouvelle
  surface — aucune migration nécessaire). Contrairement aux autres entrées
  de cette table, ni `DIRT` ni `SABLE` n'ont été observés littéralement dans
  un appel PMU réel — ajoutés par anticipation pour les futures réunions
  internationales sur piste en terre/sable ; seules de futures courses où
  PMU enverrait réellement `DIRT`/`SABLE` bénéficieraient automatiquement de
  ce mapping (le code reçu, pas le nom de la course, détermine la surface).
  **Correction ponctuelle des données demandée et effectuée (2026-07-11)** :
  les 5 courses R8 déjà collectées avec le mauvais code PMU (`GAZON` au lieu
  de `DIRT`, cf. ci-dessus) ont été corrigées manuellement en base
  (`surface_id` -> `Dirt`), sur la seule base du texte `DIRT` explicitement
  présent dans leur nom (`(2 YO - DIRT)`, etc.) — exception ponctuelle et
  assumée à la règle « ne fais aucune hypothèse », faite à la demande
  explicite de l'utilisateur pour ce cas précis, pas une nouvelle logique
  automatique généralisée à toutes les collectes futures.

## Limites connues du module Statistiques (documentées, pas cachées)

- 6 types de pari sont contrôlés contre un rapport réel (Simple Gagnant/Placé,
  Couplé Gagnant/Placé, 2 sur 4, Quinté Flexi, cf. ci-dessus) ; tout autre type
  rencontré est journalisé et ignoré, pas deviné. Couplé Gagnant/Placé, 2 sur 4
  et Quinté Flexi ne sont réellement disponibles côté PMU que sur les courses
  Quinté+ (vérifié le 2026-07-08) — un pari de ce type généré sur une course
  ordinaire ne trouve jamais de rapport correspondant, journalisé et ignoré.
- Quinté Flexi ne joue jamais en « Ordre » (nos tickets ne committent jamais un
  ordre d'arrivée) — seul le rapport Désordre + Bonus 4sur5/Bonus 3 est
  exploité ; le dividende Ordre (bien plus élevé) n'est jamais visé.
- Le remboursement réglementaire PMU quand un partant joué devient non-partant
  après l'analyse n'est pas modélisé (règles pari-mutuel non triviales, non
  vérifiées) : traité simplement comme un pari perdant si son numéro/sa
  combinaison ne correspond à aucune combinaison gagnante.
- `statistique_pari` s'appuie sur `controle_roi_pari` (une ligne par pari, cf.
  ci-dessus) — corrigé le 2026-07-08, plus de double-comptage même quand une
  analyse produit plusieurs types de pari.
- `statistique_modele` est alimentée par **deux** mécanismes distincts avec des
  sémantiques différentes de `version_modele` : `calculer_modeles()` (agrégation
  des analyses déjà persistées, groupées par `analyses.version` — un statut
  Pré/Finale, pas une version de modèle) et `scripts/rejouer_versions.py` (vrai
  rejeu multi-versions L031.7 §4-5, `version_modele` = chaîne libre décrivant
  le jeu de poids testé) — cf. « Moteur de rejeu/backtesting » ci-dessus pour
  le détail et les limites du second (Presse non rejouable, Value/Contexte non
  produites, seuils de décision non rejouables, pas de validation
  hors-échantillon automatisée).
- Pas de purge/archivage des lignes historisées dans les 6 tables statistiques —
  chaque exécution de `scripts/calculer_statistiques.py` ajoute une nouvelle
  ligne par table (cf. L030.4 §10, volontaire), mais rien ne limite leur nombre
  dans le temps.

**Double bug de duplication corrigé (2026-07-10)** : retour utilisateur — « je
ne comprends rien aux scores par tranches, idem par hippodrome et tous les
autres car je pense qu'il y a des duplications ». Vérifié réel, deux causes
distinctes cumulées :
1. Une course réanalysée plusieurs fois avant son départ (L033, automatisation
   horaire à version croissante) était comptée une fois **par version**
   historique dans `calculer_globale`/`calculer_scores`/`calculer_hippodromes`/
   `calculer_disciplines`/`calculer_paris`/`calculer_modeles` — vérifié en
   base : les courses 146 et 147 avaient chacune 4 lignes `controle_roi` (une
   par version 1 à 4) au lieu d'une seule, gonflant `nb_courses`/mises/gains
   d'autant. `list_analyses_sans_controle_roi` (`AnalyseRepository`) créait ces
   doublons en amont. Corrigé en restreignant partout à
   `a.version = (SELECT MAX(a2.version) FROM analyses a2 WHERE a2.course_id = a.course_id)`
   (constante `_DERNIERE_VERSION_COURSE` dans `StatistiqueRepository`).
2. Chaque recalcul horaire (3ᵉ étape de l'automatisation, cf. ci-dessus)
   **ajoute** une ligne par table sans jamais remplacer l'ancienne (L030.4
   §10, volontaire pour l'audit) — mais les `list_*` de `StatistiqueRepository`
   renvoyaient tout l'historique accumulé au lieu du dernier calcul, affichant
   des dizaines de lignes quasi identiques après quelques heures
   d'automatisation. Corrigé : `list_globale` ne renvoie plus que la dernière
   ligne (`ORDER BY date_calcul DESC LIMIT 1`) ; `list_scores`/`list_hippodromes`/
   `list_disciplines`/`list_paris`/`list_modeles` utilisent désormais
   `DISTINCT ON (groupe) ... ORDER BY groupe, cree_le DESC` (une ligne par
   tranche de score / hippodrome / discipline / type de pari / version, la plus
   récente) via le nouvel helper `_list_dernier_par_groupe`.

Vérifié contre PostgreSQL réel après correctif : `statistique_globale` a 6
lignes historisées, `list_globale()` n'en renvoie plus qu'1 ; `statistique_hippodrome`
a 8 lignes pour seulement 2 hippodromes distincts, `list_hippodromes()` n'en
renvoie plus que 2. `calculer_globale()`/`calculer_hippodromes()` ne comptent
plus plusieurs fois les courses 146/147.

**Nettoyage des données obsolètes effectué (2026-07-10)** : les 6 lignes
`controle_roi` (et leurs `controle_roi_pari` associés) attachées aux versions
non-finales des courses 146/147 (analyses 502/508/520 et 503/521/526) ont été
supprimées. `turfia_app` n'a volontairement pas le droit `DELETE` sur ces
tables (cf. `sql/schema/06_grants.sql`, principe du moindre privilège) ; la
suppression a été faite avec le rôle `turfia_migration` (propriétaire des
tables). Chaque course ne conserve plus qu'un seul `controle_roi`, celui de sa
dernière version.

**Point restant, non corrigé** (hors périmètre de cette demande, à surveiller) :
la course 200 a un `controle_roi` attaché à sa version 3, mais sa version la
plus récente est désormais 7 (réanalysée après coup) — avec le correctif, elle
est donc exclue des statistiques tant qu'aucun `controle_roi` n'existe pour sa
version 7. Comportement cohérent avec la règle « dernière version uniquement »
mais signale une question distincte (une course ne devrait normalement plus
être réanalysée après que son résultat a été contrôlé) — non résolu ici, pas
demandé par l'utilisateur.
Tests : `tests/integration/test_api_statistiques.py::test_list_globale_ne_montre_que_le_dernier_calcul`,
`test_list_hippodromes_ne_montre_que_le_dernier_calcul_par_hippodrome`,
`test_list_scores_ne_montre_que_le_dernier_calcul_par_tranche`.

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
- **Corrigé (2026-07-09)** : POST/PATCH sur `course` référençant un
  `discipline_id`/`type_course_id`/`distance_id`/`surface_id`/`etat_piste_id`
  inconnu retourne désormais un 404 ciblé (`_valider_referentiels_course`,
  cf. `api/routes/courses.py`) plutôt qu'une violation de contrainte FK brute
  (500) — même principe que `jockey_id`/`entraineur_id` sur un partant.
  Nouvelles méthodes `get_discipline/get_type_course/get_distance/get_surface/
  get_etat_piste` sur `ReferentielRepository` (vérifiées réellement contre
  PostgreSQL). Fait en préalable à l'interface HTML locale (meilleurs messages
  d'erreur dans les futurs formulaires).

## Explicitement hors périmètre (travail futur, non implémenté)

- Automatisations planifiées (L017/L033) — **redimensionné volontairement
  (2026-07-09)** : pour un usage mono-utilisateur local, un vrai scheduler
  générique dans le process API n'apporte rien — remplacé par de simples
  déclenchements manuels (page Administration, `POST /administration/
  automatisations/*`) plutôt qu'une planification récurrente configurable en
  base. **Premier vrai besoin de planification couvert le 2026-07-10** :
  les cotes PMU se publiant progressivement (vérifié réellement, cf. ci-dessus
  §« Limites connues de la collecte »), l'utilisateur veut relancer collecte
  + analyse toutes les heures de 9h à 14h. Nouveau
  `scripts/rafraichir_et_analyser_jour.py` (enchaîne les deux, mêmes services
  que l'Administration HTML, cf. L033 ADR-002 ; chaque étape tracée dans
  `tache`, visible dans l'Administration comme un déclenchement manuel) +
  `automations/launchd/com.turfia.rafraichir-analyser.plist` (agent `launchd`
  natif macOS, 6 exécutions 9h-14h) — exactement la solution déjà anticipée
  dans la décision du 2026-07-09 (« tâche `launchd`/cron locale appelant les
  scripts déjà existants »), pas un nouveau scheduler générique dans
  l'application. `automations/` reste un squelette Python vide (l'exécution
  planifiée passe par l'OS, pas par un module `automations/*` en tâche de
  fond) — voir `automations/launchd/README.md` pour l'installation.
  **Tableau de bord Cron ajouté le 2026-07-10** (page Administration, bloc
  avant « Automatisations ») : `TacheRepository.get_derniere_par_nom`,
  `GET /administration/cron` (dernière exécution connue de chaque tâche
  quotidienne fixe — `collecte_programme_jour`/`analyse_courses_jour` —,
  volontairement sans historique/archive), `GET /administration/cron/journal`
  (dernières 200 lignes des fichiers `logs/rafraichir_et_analyser*.log` du
  plist launchd). **Bug réel trouvé et corrigé le 2026-07-10 en vérifiant la
  route contre les données réelles** : à partir de la 2ᵉ exécution horaire du
  jour, `analyse_courses_jour` remontait systématiquement en `echec` (`Une
  analyse existe déjà pour la course N en version 1` comptée comme erreur
  pour chaque course déjà analysée à l'heure précédente — le SAVEPOINT de
  `AnalyseRepository.create_analyse` évite bien le crash du lot, mais le
  compte d'erreurs qui en résultait faisait quand même passer tout le run en
  `echec`, alors que c'est le cas attendu d'un script relancé toutes les
  heures). Corrigé en amont plutôt qu'en aval : nouvelle
  `AnalyseRepository.existe_analyse(course_id, version)` +
  `AnalyseService.deja_analysee`, appelée par `AutomatisationService.
  analyser_courses_du_jour` avant de refaire le travail de préparation —
  les courses déjà analysées sont désormais comptées à part
  (`RapportAnalyseJour.nb_deja_analysees`, affiché dans le résumé
  Administration et dans le tableau de bord Cron) et n'affectent plus le
  statut de la tâche. Vérifié réellement (script direct, transaction
  annulée) : sur les 55 courses du jour, 41 déjà analysées désormais
  ignorées proprement, seules les 14 vraies erreurs « Aucun partant
  exploitable » (déjà vérifiées légitimes, cotes PMU pas encore publiées)
  restent comptées — `nb_erreurs` passe de 55 à 14, statut `succes` dès que
  ces 14 courses obtiennent leurs cotes.
- **Passe esthétique sur les 5 pages HTML, 2026-07-10** (retours utilisateur
  après premiers tests manuels réels) :
  - Format horaire unifié `JJ/MM/AAAA - HH:MM` partout où une valeur ISO a un
    composant heure (`formaterDateHeure`/`MOTIF_DATE_ISO` déplacés dans
    `api.js`, chargé par toutes les pages, plutôt que dupliqués — utilisés
    désormais aussi par historique.js/statistiques.js/course.js/accueil.js,
    pas seulement administration.js). Les dates seules (jour de réunion, sans
    heure) restent en `AAAA-MM-JJ`, non concernées.
  - Toute analyse affichée porte désormais son heure de calcul
    (`date_calcul`) : fiche course (liste + détail), page Accueil (bloc
    paris), page Historique (nouvelle colonne « Analysée le »). Nécessitait
    d'ajouter `date_calcul` à `HistoriqueLigne`/`HistoriqueLigneOut` (absent
    jusqu'ici, cf. `HistoriqueRepository._COLONNES`) — vrai gap, pas juste un
    oubli d'affichage.
  - Page Accueil : nom d'hippodrome affiché (`Reunion.hippodrome_nom`, LEFT
    JOIN `hippodrome` ajouté à `CourseRepository.get_reunion`/
    `list_reunions_by_date`) au lieu de « hippodrome #N ». Nouveau filtre
    hippodrome (`GET /reunions?hippodrome_id=`, réutilise `/hippodromes` déjà
    utilisé par Historique). Nouveau filtre décision Jouer/Ne pas jouer/Toutes,
    actif par défaut sur « Jouer » (masque les courses `Ne pas jouer` et les
    courses pas encore analysées ; une réunion sans aucune course
    correspondante est masquée entièrement plutôt que montrée vide).
  - Page Historique : bloc de filtres réorganisé en deux colonnes (`.colonnes-
    deux`, empilées sur petit écran) — filtres à gauche, rappel des règles de
    décision à droite (seuils de score → décision/budget, cf. `src/algorithms/
    score.py::determiner_decision`, `src/algorithms/classement.py::
    calculer_budget` — texte statique, valeurs recopiées des constantes
    réelles du code, pas inventées).
  - Vérifié réellement contre PostgreSQL (pas seulement via les tests sur
    fakes) : `list_reunions_by_date` renvoie bien les noms d'hippodrome réels
    (ex. « HIPPODROME DE CABOURG »), le filtre `hippodrome_id` réduit
    correctement le résultat, `HistoriqueRepository.rechercher` renvoie
    `date_calcul` peuplé. Limite honnête : pas de navigateur pour valider
    visuellement le rendu JS — vérifié par lecture du code + réponses API
    réelles, comme pour le reste de l'interface HTML.
- **Deuxième passe esthétique, 2026-07-10** (mêmes retours utilisateur) :
  - Tous les montants en euros affichés dans l'interface ont désormais un
    séparateur de milliers " " (`formaterMontant` dans `api.js`, partagé) —
    budgets/mises/gains/profits/drawdown, sur les 4 pages concernées
    (Accueil, fiche course, Historique, Statistiques). Séparateur décimal
    laissé en "." (demande limitée au séparateur de milliers). Vérifié
    directement en Node (hors navigateur) sur les cas limites (négatif, zéro,
    plusieurs milliers).
  - Tableau de bord Cron (Administration) : nouvelle colonne « Prochain
    déclenchement » avec compte à rebours réel (`HH:MM:SS`, mis à jour chaque
    seconde par `setInterval`) + heure absolue du prochain créneau. Calculé
    entièrement côté client à partir de la planification `[9, 10, 11, 12, 13,
    14]` (dupliquée en JS depuis `automations/launchd/com.turfia.rafraichir-
    analyser.plist`, volontairement — un compte à rebours client reste exact
    même après l'heure de déclenchement passée, contrairement à un instant
    figé récupéré une fois depuis le serveur). Vérifié en Node sur les cas
    limites (avant 9h, entre deux créneaux, juste après 14h, tard le soir).
  - Page Administration : les 7 blocs (`Supervision`/`Tableau de bord Cron`/
    `Automatisations`/`Sauvegardes`/`Versions publiées`/`Paramètres`/
    `Journaux`) sont désormais des `<details class="carte">` repliés par
    défaut — tout le bandeau (`<summary><h2>`) est cliquable pour déplier,
    comportement natif du navigateur (pas de JS ajouté pour le toggle lui-même,
    seul le CSS `::before`/`[open]` gère le chevron). Le chargement des
    données de chaque bloc reste déclenché au chargement de la page comme
    avant : un `<details>` fermé garde son contenu dans le DOM (juste masqué
    visuellement), donc les données sont déjà prêtes à l'ouverture.
- **Troisième passe, 2026-07-10** (mêmes retours utilisateur) :
  - Jauge « temps avant le départ » pour toute course pas encore partie
    (Accueil, fiche course) : badge coloré (dégradé continu vert -> rouge,
    rouge plein sous 30 min, vert plein au-delà de 90 min), texte "HH:MM
    (dans Xh MM)", rafraîchi toutes les 30 s côté client (`construireBadgeDepart`/
    `couleurJaugeDepart` dans `api.js`, partagés). Vérifié en Node sur les
    seuils (5/29/30/45/60/89/90/120/180 min).
  - **Vrai bug trouvé et corrigé : le déclenchement manuel d'analyse
    (fiche course, `POST /courses/{id}/analyses/auto`) échouait quasi
    systématiquement.** `html/static/js/course.js` n'envoyait jamais de
    `version` dans le payload -> l'API utilisait toujours le défaut
    `AnalyseAutoIn.version = 1`. Or l'automatisation horaire
    (`analyse_courses_jour`) crée déjà une analyse en version 1 pour
    quasiment toutes les courses du jour (cf. tableau de bord Cron) — tout
    déclenchement manuel ultérieur retombait donc sur la même version et
    recevait 409 (« Une analyse existe déjà… »), rendant le bouton « lancer
    une analyse » de facto inutilisable après le premier passage du cron.
    Corrigé en visant systématiquement, côté JS, la version suivant la plus
    haute déjà connue pour la course (`GET /courses/{id}/analyses` avant
    soumission) — jamais de conflit, l'analyse peut être relancée « quand on
    veut » à tout moment. Aucune modification API nécessaire (la logique de
    versionnement existait déjà, seul l'appelant JS ne s'en servait pas).
    Vérifié réellement contre PostgreSQL (script direct, transaction
    annulée) : rejouer la version 1 d'une course déjà analysée échoue bien
    (409), viser la version 2 réussit. Fake `AnalyseRepository.create_analyse`
    (tests) ne reproduisait pas non plus la contrainte UNIQUE(course_id,
    version) réelle — corrigé en même temps, sinon ce bug serait resté
    invisible à la suite de tests.
- **Quatrième passe, 2026-07-10** : re-analyse horaire à version toujours
  croissante (la décision peut changer dans les deux sens) + vrai bug de
  construction des paris trouvé et corrigé.
  - `AutomatisationService.analyser_courses_du_jour` ne s'appuie plus sur une
    `version` fixe passée par l'appelant : chaque course reçoit systématiquement
    `AnalyseService.prochaine_version(course_id)` (= max version existante + 1),
    comme le déclenchement manuel (cf. ci-dessus). Le paramètre `version` a été
    retiré de la méthode, de `POST /administration/automatisations/analyse-jour`
    et du schéma `AnalyseAutoIn` (`analyses/auto` ignore désormais tout
    `version` fourni — toujours la version suivante, cf. `AnalyseRepository.
    get_derniere_version`). Une course dont l'heure de départ est déjà passée
    est ignorée (`RapportAnalyseJour.nb_deja_parties`, renommé depuis
    `nb_deja_analysees` — son sens a changé : plus "déjà analysée à cette
    version" mais "déjà partie", les paris étant clos) plutôt que réanalysée
    inutilement.
  - `scripts/rafraichir_et_analyser_jour.py` + `automations/launchd/
    com.turfia.rafraichir-analyser.plist` : fenêtre de déclenchement élargie à
    9h-23h (large, pour couvrir les réunions en nocturne — vérifié réellement
    qu'une dernière course peut partir à 22h13) ; c'est le script lui-même qui
    n'exécute l'étape d'analyse que si on est à plus de 30 minutes de la
    dernière course réelle du jour (`CourseRepository.get_derniere_heure_depart`),
    sinon il journalise un passage "hors fenêtre" sans rien recalculer — la
    collecte, elle, continue de tourner à chaque passage. Agent réinstallé
    (unload/copy/load) pour appliquer la nouvelle planification.
  - **Vrai bug trouvé (indépendamment demandé par l'utilisateur) et corrigé :
    une décision "Jeu prudent"/"Jeu normal" pouvait recommander un budget sans
    proposer aucun pari pour le dépenser.** `categoriser` (seuils Base ≥85/
    Chance régulière ≥70, cf. L031.6 §4, qualitatifs dans le SAD) est
    indépendant des paliers de budget (60/75/85, cf. L031.6 §6) : une tête de
    liste avec un score final entre 60 et 70 engage un budget de 10 € sans
    forcément atteindre "Chance régulière", et `construire_paris` ne
    construisait alors aucun pari (ne regarde que les catégories Base/Chance
    régulière). Vérifié réellement en base : 2 analyses "Jeu prudent"/10 €,
    0 ligne dans `pari`. Corrigé dans `construire_paris` : si aucune Base ni
    Chance régulière n'existe du tout, un Simple Placé de secours est
    construit sur la tête de liste (jamais Simple Gagnant, réservé à une
    vraie Base) — sans changer sa catégorie affichée. Re-vérifié sur le même
    cas réel (course 200, script direct, transaction annulée) : 1 pari Simple
    Placé de 10 € désormais proposé.
  - **Vrai bug trouvé (retour utilisateur : « c'est quoi ces numéros de
    partant et quelle est la combinaison à jouer ? ») et corrigé : la fiche
    course affichait des `partant_id` bruts (identifiants techniques, ex.
    « 2130 ») au lieu du numéro de course et du nom du cheval — inexploitable
    pour placer un pari réel.** Concerne 3 endroits : le tableau des partants
    d'une analyse (colonne « Partant »), la sélection d'un pari (`Pari.
    combinaison`, une liste de `partant_id` jointés par des tirets, ex.
    « 2130 »), et le tableau des résultats d'arrivée (colonne « N° »).
    Corrigé en joignant `CourseRepository.list_partants_detail_by_course`
    (déjà utilisé pour la fiche partant, pas de nouvel N+1) : `AnalysePartantOut`
    gagne `numero`/`cheval_nom`, `ParisOut` gagne `combinaison_lisible` (ex.
    « N°1 SOMMERKONIG »), affichés par `course.js` (partants/paris/résultats)
    et `accueil.js` (bloc paris) à la place des identifiants bruts — `Pari.
    combinaison` reste inchangé en base (référence technique). Vérifié
    réellement contre le cas exact remonté par l'utilisateur (analyse #489,
    course 200) : `partant_id=2130` -> « N°1 SOMMERKONIG », le pari Simple
    Placé affiche désormais cette même sélection au lieu de « combinaison
    2130 ». Vérifié aussi sur un vrai tableau de résultats d'arrivée
    (course 114).
- **Cinquième passe, 2026-07-10** : filtre décision Accueil élargi + raccourci
  "courses imminentes".
  - Le filtre décision de l'Accueil devient un choix multiple (cases à cocher,
    `#filtre-decision-accueil`) sur les 4 décisions réelles (cf.
    `src/core/constants.py::DECISIONS` : Ne pas jouer/Jeu prudent/Jeu normal/
    Forte opportunité), plus seulement un choix binaire jouer/ne pas jouer.
    Par défaut à l'ouverture : tout coché sauf "Ne pas jouer" (même
    comportement qu'avant, exprimé différemment). Une course pas encore
    analysée (aucune décision) n'est affichée que si les 4 cases sont
    cochées (pas de filtrage réel) — cohérent avec l'ancien comportement de
    l'option "Toutes".
  - Nouveau bouton "Courses à jouer dans l'heure" : force la date du jour et
    les décisions ("tout sauf Ne pas jouer"), puis ajoute un filtre
    départ ≤ 60 minutes (`departImminent`, calcul client, pas d'appel réseau
    supplémentaire — le filtre s'applique avant même de charger l'analyse
    d'une course exclue). Bouton à bascule (état visuel actif/inactif) ;
    toute modification manuelle des filtres désactive le raccourci pour
    éviter un état visuel trompeur. Vérifié en Node sur les seuils (30 min/
    90 min/départ déjà passé). Confirmé : le choix multiple est bien une
    condition « ou » (`decisions.includes(decision)`, cf. `accueil.js`), pas
    un « et » — déjà le comportement implémenté, pas de changement nécessaire.
  - **Vrai bug trouvé (retour utilisateur : « tu dois calculer les ROI sur
    toutes tes propositions de jeux ») et corrigé : le ROI théorique
    (`Analyse.roi_theorique`, `Pari.roi_estime`) était presque toujours proche
    de -90 %, quelle que soit la vraie valeur du pari.** `AnalyseService.
    analyser_course` appelait `esperance(p_turfia, rapport_estime=p.cote,
    mise=mise_reference)` — `rapport_estime` doit être le gain total attendu
    en euros pour la mise réellement engagée (cf. L031.4 §5 : « Espérance =
    Probabilité_TurfIA × Rapport_estimé − Mise »), soit `mise_reference *
    p.cote`, pas `p.cote` seul (une cote décimale sans dimension). L'ancien
    calcul mélangeait les deux, avec `p_turfia × cote` (typiquement < 3)
    presque toujours écrasé par `- mise_reference` (10 par défaut), donnant un
    ROI quasi systématiquement ≈ -90 % à -100 % indépendamment de la vraie
    valeur du pari. Corrigé (une ligne) ; propriété vérifiée par test : le ROI
    (un pourcentage) est désormais indépendant de `mise_reference` (invariant
    mathématique qui n'était pas respecté avant, cf. `tests/integration/
    test_analyse_service.py::test_roi_theorique_independant_de_la_mise_reference`).
    Référence figée de non-régression (L020 §8.3) régénérée en conséquence
    (`tests/fixtures/reference_analyse_non_regression.json`, raison
    documentée dans le fichier). Vérifié réellement contre PostgreSQL (course
    200, transaction annulée) : ROI éclatés et plausibles (-52 % à +116 %
    selon les partants) au lieu d'un bloc uniforme ≈ -85 %.
  - **Nouvelle capacité : récupérer les résultats d'une course spécifique
    après son départ, à la demande**, sans attendre le prochain passage de la
    collecte horaire (qui couvre déjà tout le programme du jour, cf.
    `CollecteService.collecter_programme_du_jour` — les résultats y sont déjà
    extraits via `extraire_classement` sur le même appel PMU `/participants`)
    ni ré-importer tout le programme pour une seule course. Nouvelle méthode
    `CollecteService.collecter_resultats_course(course_id)` (réutilise
    `_importer_partant`, get_or_create donc idempotent) + route `POST
    /courses/{id}/resultats/collecter` (rôle `DECLENCHEMENT_ANALYSE`, même
    tier que le déclenchement d'analyse) + bouton « Récupérer les résultats »
    sur la fiche course (visible en permanence, pas seulement quand des
    résultats existent déjà). Vérifié réellement contre l'API PMU (course
    114, déjà arrivée) : 8 partants traités, 8 résultats en base avant/après
    (idempotent, aucun doublon), transaction annulée.
  - **Vrai bug trouvé (retour utilisateur, capture d'écran du journal
    Administration : rafale de WARNING « Rapports PMU indisponibles ») et
    corrigé.** `ControleRoiService.calculer_controles_manquants()` retentait,
    à chaque déclenchement de « Calculer les statistiques », le contrôle ROI
    de TOUTES les analyses sans `controle_roi` — y compris celles dont la
    course n'était pas encore partie ou venait tout juste de partir (rapports
    définitifs PMU pas encore homologués), échouant à tous les coups et
    journalisant le même WARNING en boucle pour les mêmes courses (constaté
    réellement : 3 courses R6C8/R7C1/R7C2, départs 19h50/18h30/19h00, alors
    qu'il était 18h37). Corrigé : une course dont le départ est inconnu (`None`,
    comportement historique préservé) est traitée comme avant, mais une
    course dont le départ est connu et à moins de 15 min (passés ou à venir,
    `MARGE_HOMOLOGATION_MINUTES`) est ignorée en amont, sans appel PMU ni
    WARNING — les rapports ne peuvent de toute façon pas encore exister.
    Vérifié réellement (transaction annulée) : 9 analyses candidates avant
    filtre, 4 réellement tentées et calculées avec succès, 0 WARNING (contre
    plusieurs dizaines observées dans le journal avant ce correctif).
  - **Vrai bug trouvé (retour utilisateur : « tu dupliques les courses ») et
    corrigé : la page Historique montrait une ligne par VERSION d'analyse,
    pas une ligne par course.** `HistoriqueRepository.rechercher` joignait
    `analyses a ON a.course_id = c.id` sans filtrer sur la version — une
    course réanalysée plusieurs fois dans la journée (cf. L033, chaque passage
    horaire vise une nouvelle version) apparaissait donc une fois par version
    calculée. Corrigé : la jointure ne retient que `a.version = MAX(version)`
    par course (sous-requête corrélée). Vérifié réellement : 111 lignes -> 47
    lignes sur les données du jour, 0 course avec plusieurs versions dans le
    résultat (contre 19 avant correctif, jusqu'à 5 versions pour une même
    course).
  - Filtre décision de l'Historique élargi en choix multiples (mêmes cases à
    cocher qu'Accueil, "ou" logique), par défaut tout sauf "Ne pas jouer" —
    `HistoriqueFiltres.decision` (singulier) devient `decisions: list[str]`,
    `GET /historique?decisions=...` accepte plusieurs valeurs répétées
    (`a.decision = ANY(%s)` côté SQL). Colonne « Version » retirée du tableau
    (une seule version affichée désormais, l'information n'apporte plus rien
    à cette vue — l'historique complet des versions reste sur la fiche course).
  - **Réponse à « quand as-tu les résultats définitifs avec les gains ? »** :
    jusqu'ici, uniquement de façon manuelle (bouton « Calculer les
    statistiques » de l'Administration, ou `python scripts/
    calculer_statistiques.py`) — décision explicite du 2026-07-09 (« pas
    d'intégration à un ordonnanceur dans cette tranche »). **Revu à la demande
    de l'utilisateur (2026-07-10, "oui")** : `scripts/
    rafraichir_et_analyser_jour.py` gagne une 3ᵉ étape (`calcul_statistiques`,
    même tâche/nom que le déclenchement manuel) qui enchaîne
    `ControleRoiService.calculer_controles_manquants()` (désormais filtré,
    cf. ci-dessus — ignore silencieusement les courses trop récentes) puis
    `StatistiqueService.calculer_toutes()`, à chaque passage horaire (9h-23h,
    sans fenêtre de coupure contrairement à l'analyse : cette étape est
    justement utile pour les courses déjà parties). `calcul_statistiques`
    ajoutée à `TACHES_QUOTIDIENNES` (tableau de bord Cron). Cela ne revient
    pas sur la décision du 2026-07-09 (pas de scheduler générique) : c'est la
    même réutilisation d'un script CLI déjà existant que pour les deux
    premières étapes (cf. L033 ADR-002). Vérifié réellement en conditions de
    production (launchd, pas un test) : les 3 tâches s'enchaînent et se
    terminent en succès (`collecte_programme_jour`, `analyse_courses_jour`,
    `calcul_statistiques`, tables recalculées), visibles dans le tableau de
    bord Cron.
- **Diagnostic demandé par l'utilisateur (« quasiment aucune course n'est
  jouable, redonne-moi la méthode de calcul du score de confiance ») —
  vrai bug trouvé et corrigé, en plus de l'explication.**
  - Score de confiance = score final de la tête de liste après classement
    (cf. L031.1 §9, `AnalyseService.analyser_course`) = Score TurfIA + Bonus
    Value Bet (5 si value bet) − Malus Risque (0,2 × risque, cf. L031.6 §3).
    Score TurfIA = moyenne pondérée des sous-scores des familles réellement
    présentes pour ce partant (poids par défaut tous à 1,0, paramétrables via
    `parametre.poids_score.*`) — une famille absente (ex. Presse hors
    Quinté+) est exclue de la moyenne, pas comptée comme neutre.
  - **Vrai bug trouvé en creusant pourquoi le score reste bas : la famille
    "Forme" valait le score neutre (50) pour 100 % des partants, tout le
    temps.** `CollecteService._importer_partant` n'a jamais extrait le champ
    `musique` des données PMU (`participant_brut.get("musique")` absent du
    code) alors que la donnée existe bien réellement (vérifié par un appel
    PMU réel : `"0aDa2a2a2a(25)Da1a4aDm"` pour un partant) — `calculer_
    indicateur_forme` recevait donc systématiquement `None` et retournait le
    score neutre. Vérifié réellement en base : 0 partant sur 609 avec une
    musique renseignée. Corrigé : `musique` extraite et portée par `Partant`
    (pas `Cheval` — la musique reflète l'historique du cheval tel que connu
    pour CETTE course précise, jamais écrasée entre courses) ;
    `PreparationDonneesService` lit désormais `partant.musique` (supprime au
    passage un `get_cheval` par partant, plus nécessaire). N'affecte que les
    NOUVEAUX partants collectés à partir de maintenant (`get_or_create_partant`
    ne met jamais à jour une ligne déjà existante, cf. `ON CONFLICT ... DO
    NOTHING`) — les partants déjà collectés aujourd'hui restent sans musique
    tant qu'ils ne sont pas re-collectés depuis zéro.
  - Concrètement, avec ce bug, sur une course réelle à 15 partants observée
    en vérifiant ce diagnostic (course 150) : Forme = 50 et Professionnels ≈
    50 pour tous, Historique = 41,7 pour tous (identique par hippodrome, peu
    de données réelles accumulées à ce stade) — seul Marché variait vraiment.
    Un seul partant (le favori du marché) dépassait tout juste le seuil de
    60 (score 60,4) ; tous les autres restaient sous 52. Une fois "Forme"
    réellement alimentée, ce goulot d'étranglement s'atténue mécaniquement
    (plus une seule famille sur 3-4 disponibles porte l'information) — mais
    "Historique"/"Professionnels"/"Aptitude" resteront proches du neutre tant
    que peu de courses réelles auront été contrôlées (`controle_roi`) et que
    peu de statistiques jockey/entraîneur/cheval-dans-ces-conditions auront
    atteint le seuil minimal de 3 courses (cf. `calculer_indicateur_reussite`,
    `calculer_indicateur_historique_moteur`) — pas un bug, une limite de
    démarrage qui se résorbe avec l'accumulation de données réelles.
  - **Suite au retour utilisateur (« si si peu de courses sont jouables,
    c'est qu'il y a un autre souci » + comparaison à un concurrent obtenant
    75/100 « jouer normalement » sur le même Quinté+) : vrai bug d'incohérence
    trouvé et corrigé dans le calcul du Score TurfIA lui-même**, au-delà du
    bug `musique` ci-dessus. Une famille réellement absente (ex. Presse hors
    Quinté+) était déjà exclue de la moyenne pondérée — mais une famille
    présente dont l'échantillon est statistiquement insuffisant (`nb_courses
    < minimum_courses`, cf. `calculer_indicateur_reussite`/`calculer_
    indicateur_historique_moteur`) ou dont la musique est absente (cf.
    `calculer_indicateur_forme`) retombait à un score neutre (50) compté à
    PLEIN POIDS dans la moyenne — traitement incohérent de deux situations
    pourtant équivalentes (« je ne sais pas »), qui diluait systématiquement
    le score dès qu'une famille manquait de données suffisantes (quasiment
    toujours en tout début de vie du moteur : peu d'hippodromes/jockeys/
    entraîneurs ont encore 3 courses réelles contrôlées). Ni un bug SAD (L031.2
    §5 est muet sur la gestion des échantillons insuffisants, aucune formule
    n'y est imposée) ni une recalibration des pondérations (inchangées,
    toutes à 1,0 — cf. L031.2 §10, toute pondération doit être validée sur
    historique avant adoption, ce que le peu de données réelles actuelles ne
    permet pas encore) : uniquement une correction de cohérence interne, déjà
    appliquée à "aptitude"/"presse" absents, désormais étendue à "forme" (cf.
    `calculer_indicateur_forme` retourne `None` si aucune musique),
    "professionnels" (`calculer_indicateur_professionnels` exclut les
    variables `None`, `None` si les 3 le sont) et "historique". Corrigé dans
    `src/algorithms/indicateurs.py` (signatures `float | None`) et
    `PreparationDonneesService` (n'ajoute la clé au dict `sous_scores` que si
    la valeur n'est pas `None`).
  - Vérifié réellement (transaction annulée) : sur la même course 150 utilisée
    pour le diagnostic, le meilleur score passe de 57,9 à 60,6 (franchit
    « Jeu prudent »). Sur le Quinté+ réel du jour (course 109, avec un vrai
    consensus presse Canalturf/Zone-Turf) : le partant en tête atteint
    désormais **81,7 (« Jeu normal »)**, un second à 72,0 — directement
    comparable à l'ordre de grandeur cité par l'utilisateur (75/100, « jouer
    normalement ») pour un système concurrent sur le même type de course,
    alors qu'avant ce correctif la dilution systématique aurait plafonné ce
    même partant nettement plus bas.
  - **Vérification de bout en bout (2026-07-10, ~21h06)** : automatisation
    horaire relancée manuellement après le correctif (pas d'attente du
    prochain passage). Preuve directe en base : la course 152 passe de
    « Ne pas jouer » (score 49,52, version 4, calculée à 21h00 avant le
    correctif) à **« Jeu prudent » (score 62,57, version 5, calculée à
    21h06 après le correctif)** — même course, mêmes cotes, seul le calcul a
    changé. Étape statistiques également relancée (tables recalculées, 0
    nouveau contrôle ROI cette fois — aucune analyse fraîchement éligible).
    **Limite honnête** : la course 109 (le Quinté+ cité plus haut) était déjà
    partie au moment de cette relance — son analyse reste figée sur sa
    dernière valeur calculée *avant* le correctif (une course déjà courue
    n'est plus jamais réanalysée, cf. `nb_deja_parties` ci-dessus) ; le score
    81,7 cité est celui d'un calcul à blanc (transaction annulée) avec le
    code corrigé sur les mêmes données, pas (encore) la valeur persistée
    officiellement pour cette course précise.
  - **Méthode de calcul documentée dans le SAD lui-même** (pas seulement ici) :
    cf. `docs/L031.2_ALGORITHMES_SCORE_TURFIA_v1.0.md` §6.1 (nouveau,
    version 1.2 du document) — règle d'exclusion des familles sans donnée
    exploitable, formalisée comme clarification d'implémentation plutôt que
    silencieusement laissée dans le seul code.
- **Vrai gap trouvé (retour utilisateur : « tu n'affiches nulle part les
  combinaisons de jeux avec les paris par combinaison ») et corrigé, 2026-07-10.**
  Un ticket Quinté Flexi joue en réalité TOUTES les combinaisons de 5 chevaux
  parmi la sélection retenue (Bases + Chances régulières + Outsider + Tocard
  éventuel, cf. L031.6 §5) dès que celle-ci dépasse 5 chevaux — `Pari.
  combinaison` ne stocke que le pool des chevaux sélectionnés (ex. 6 chevaux),
  jamais les `C(6,5)=6` combinaisons individuellement jouées. `combinaison_
  lisible` (ajouté plus tôt) affichait donc le pool entier comme si c'était
  une seule combinaison, sans jamais montrer les tickets réellement joués ni
  leur mise chacun. Corrigé : nouvelle fonction `_sous_combinaisons_quinte`
  (`api/routes/analyses.py`, même logique d'énumération que `ControleRoiService.
  calculer_gains_pari`, déjà réutilisée pour le calcul des gains réels — ici
  pour l'affichage) ; `ParisOut` gagne `sous_combinaisons`/`mise_par_
  combinaison` (`None` pour tout type de pari autre que Quinté Flexi, ou si la
  sélection compte déjà exactement 5 chevaux). Affiché par `course.js` (liste
  dédiée sous le tableau des paris) et `accueil.js` (sous-liste imbriquée sous
  la ligne Quinté Flexi). Vérifié par test unitaire direct (6 chevaux -> 6
  combinaisons de 5, mise totale répartie également) — aucun Quinté Flexi
  réel en base au moment de la vérification (peu de courses atteignent encore
  une sélection de 6+ chevaux, cf. les limites de démarrage documentées
  ci-dessus), donc pas de vérification bout-en-bout possible sur données
  réelles cette fois, limite assumée et signalée honnêtement.
- **Bloc "Pari" dédié sur la fiche course (retour utilisateur, 2026-07-10)** :
  jusqu'ici, le choix des combinaisons de jeu (type de pari, sélection, mise,
  combinaisons Quinté Flexi) n'était visible qu'en cliquant dans "Analyses"
  puis en sélectionnant une version — l'information la plus directement
  actionnable de la page était donc masquée par défaut. Nouvelle section
  "Pari" (`html/templates/course.html`, entre Partants et Résultat) toujours
  peuplée avec la DERNIÈRE analyse connue dès le chargement de la page, sans
  clic supplémentaire ; rafraîchie aussi après un nouveau déclenchement
  manuel d'analyse. `construireTableauParis` extrait du code déjà existant
  de `formaterDetailAnalyse` (partagé entre les deux, pas de logique
  dupliquée) — celui-ci reste inchangé pour consulter le détail complet
  (classement des partants inclus) d'une version passée au choix. Vérifié
  réellement contre PostgreSQL (course 112, analyse v9 réelle, décision
  "Jeu prudent", pari Simple Placé mise 10 €).
- **Interface HTML (L018) — les 5 modules (Accueil/Courses-Analyses/
  Statistiques/Historique/Administration) sont désormais implémentés
  (2026-07-09)** (cf. section dédiée ci-dessus). Seul le module
  Automatisations planifiées (scheduler générique récurrent) reste hors
  périmètre (cf. ci-dessous) — l'Administration livrée couvre le
  déclenchement *manuel* des mêmes opérations, pas leur planification.
- Endpoints résultats/cotes en écriture, PATCH/DELETE sur les ressources
  référentielles/métier, authentification/RBAC réels, module Statistiques
  (ROI réel + 6 tables agrégées) et moteur de rejeu/backtesting L031.7 §4-5
  sont désormais implémentés (cf. ci-dessus). Reste hors périmètre :
  administration des utilisateurs via l'API — **décidé volontairement hors
  périmètre** (2026-07-09) : l'interface HTML tourne uniquement en local sur
  la machine de l'utilisateur, un seul compte (déjà créable via
  `scripts/creer_utilisateur.py`), pas de gestion multi-utilisateurs à
  construire.
- La vraie définition L031.2 de « Historique » (performance passée du moteur
  TurfIA lui-même, par hippodrome) est désormais implémentée (2026-07-09, cf.
  « Rebranchement de la famille Historique » ci-dessus) — l'ancienne
  interprétation L031.1 (performance du cheval à l'hippodrome) a été retirée.
- Collecte de niveau 1/2 partiellement implémentée (PMU uniquement, cf. ci-dessus).
- Tous les sous-scores de `src/algorithms/score.py` sont désormais calculés
  automatiquement depuis les données collectées, à l'exception de Value et Contexte
  (non traités dans les tranches Indicateurs/Presse/Professionnels-Historique-
  Aptitude). Le risque de la course n'est approximé que par la taille du champ
  (`calculer_indicateur_risque_taille_champ`) ; les autres facteurs de risque
  documentés (volatilité du marché, désaccord presse, changement de terrain, cf.
  L031.3 §3) restent hors périmètre.
- Les requêtes `compter_performances_*` s'exécutent une par une par partant (jusqu'à
  4 requêtes SQL par partant, cf. rebranchement de la famille Historique
  ci-dessous qui en a retiré une 5e) — proportionné au volume actuel
  (déclenchement manuel), non optimisé (pas de requête groupée/matérialisée)
  si le volume devait augmenter.
- **CI/CD ajouté le 2026-07-09** (`.github/workflows/tests.yml`, GitHub
  Actions) : `pytest tests/ -q` sur chaque push/PR vers `main`/`develop` —
  aucun secret nécessaire (la suite tourne entièrement sur des repositories
  en mémoire, `tests/integration/conftest.py` fournit déjà des valeurs
  `DATABASE_URL`/`SECRET_KEY` factices). Le `Dockerfile`/`docker-compose.yml`
  restent un socle minimal — **décision explicite (2026-07-09)** : les
  durcir "pour la production" n'a plus de sens, l'app tourne strictement en
  local mono-utilisateur (cf. décisions déjà actées sur l'interface HTML/
  l'administration des utilisateurs) ; pas un report, un non-objectif.
- **Sixième passe, 2026-07-10** (retour utilisateur : « dans le bloc ROI
  global, mets la liste des paris en cours à surveiller avant leur course
  avec un lien vers la course ») : nouvelle méthode
  `HistoriqueRepository.list_paris_en_cours()` (+ `FakeHistoriqueRepository`,
  même composition course_repo/analyse_repo/referentiel_repo que
  `rechercher`) — courses dont la dernière analyse (restreinte à la dernière
  version, même raison que `rechercher`, cf. L033) engage un budget réel
  (`budget > 0`) et dont l'heure de départ n'est pas encore passée
  (`heure_depart IS NULL OR heure_depart > now()`). Nouvelle route `GET
  /historique/paris-en-cours` (`ParisEnCoursLigneOut`), nouveau modèle
  `ParisEnCoursLigne` (`src/models/historique.py`). Page Accueil : le bloc
  « ROI global » affiche désormais, sous les indicateurs, la liste de ces
  courses avec un lien direct vers `course.html?id=` (même page que le bloc
  « Pari » détaillé) — pas de nouveau bloc séparé, même sujet que le ROI
  global. Vérifié : `pytest` (4 nouveaux tests — course à venir listée,
  course déjà partie exclue, budget nul exclu, dédoublonnage par dernière
  version) ; vérifié contre PostgreSQL réel (requête directe, transaction
  annulée) — 0 ligne actuellement, cohérent avec 0 course à `heure_depart`
  future en base au moment du test (pas un bug, absence réelle de données
  futures). Limite honnête : pas de compte utilisateur de test disponible
  pour une vérification visuelle complète dans le navigateur — vérifié par
  lecture du code, `node --check`, et réponse API réelle (401 sans jeton,
  confirmant le câblage de la route).

## Prochaine étape

L'essentiel de la surface API, l'authentification/RBAC réelle, une deuxième
source de consensus presse, le module Statistiques (ROI réel + 6 tables
agrégées, granularité par pari via `controle_roi_pari`), les 6 types de pari
(Simple Gagnant/Placé, Couplé Gagnant/Placé, 2 sur 4, Quinté Flexi), l'audit
systématique des écritures (au-delà des seuls événements d'authentification)
et le moteur de rejeu/backtesting L031.7 §4-5 (`scripts/rejouer_versions.py`,
7 indicateurs, persistance légère dans `statistique_modele`) sont désormais en
place. France Galop (niveau 1) a été explorée réellement le 2026-07-08 et
écartée (cf. tableau des sources ci-dessus) : robots.txt n'y autorise que des
listes sommaires, tout le détail exploitable est interdit — le mono-source PMU
reste donc la seule source niveau 1 exploitable en l'état.

**Interface HTML locale (2026-07-09)** : les 5 modules L018 (Accueil,
Courses/Analyses, Statistiques, Historique, Administration — périmètre
complet incluant sauvegardes/supervision) sont désormais implémentés (cf.
ci-dessus), **strictement locale** (tourne uniquement sur la machine de
l'utilisateur, un seul compte) — en conséquence, l'administration des
utilisateurs via l'API et un vrai scheduler générique (« Automatisations
planifiées ») restent volontairement écartés, pas de simple report ;
l'Administration livrée ne fait que du déclenchement manuel des mêmes
opérations qu'un scheduler exécuterait.

Deux gaps réels de droits PostgreSQL ont été trouvés et corrigés en
vérification (`turfia_app` n'avait accès ni à `version` ni, pour `pg_dump`,
à `migration` — cf. migrations `20260709_1900_grant_version_turfia_app.sql`
et `20260709_2000_grant_migration_table.sql`) : à surveiller si de nouvelles
tables techniques sont ajoutées, le GRANT de `sql/schema/06_grants.sql` doit
systématiquement être étendu en même temps que le schéma.

La famille Score « Historique » a été rebranchée le 2026-07-09 sur le vrai
signal moteur (cf. « Rebranchement de la famille Historique » ci-dessus) —
Value et Contexte restent hors périmètre (aucune formule SAD documentée pour
elles non plus).

La fiche partant HTML a été enrichie le 2026-07-09 (jointure au lieu des
appels N+1, cf. ci-dessus). **Presse hors Quinté+ : impasse réelle confirmée
avec l'utilisateur (2026-07-09)**, pas une piste à rouvrir — Paris-Turf
bloque le bot Anthropic, Geny/ZEturf bloquent tout robot sur le contenu
utile (`Disallow` pronostics/fiches), et même Canalturf/Zone-Turf n'ont un
vrai consensus multi-journaux que sur le Quinté+ du jour ; aucune source
permise ne fournit de consensus presse ailleurs.

CI/CD ajouté le 2026-07-09 (GitHub Actions, cf. ci-dessus) ; le durcissement
du Dockerfile "pour la production" est désormais un non-objectif assumé
(app strictement locale).

Pistes restantes : formules pour Value/Contexte si une source documentaire
apparaît un jour (L031.5 Value Bet est un mécanisme de sélection distinct,
pas une formule de sous-score) ; un vrai scheduler si le besoin de
planification réapparaît (actuellement redimensionné en déclenchements
manuels, cf. ci-dessus) ; grouper les requêtes `compter_performances_*` si
le volume analysé augmente un jour (aucun signe actuel que ce soit
nécessaire).

## Conventions de développement

- Commits atomiques.
- Développement sur la branche develop.
- Documentation synchronisée avec le code.
- Aucune modification rétroactive des historiques.
- Respect des procédures TurfIA.

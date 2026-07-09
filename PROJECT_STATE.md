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
    `login.html` sur 401). Navigation par query string
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
  `SupervisionService`) + 118 tests d'intégration (dont Historique — filtres
  date/hippodrome/type de pari/décision — et Administration — RBAC,
  journaux, les 3 automatisations, sauvegarde réussie/échouée, versions,
  paramètres, supervision) — repositories/services en mémoire,
  `tests/integration/`), tous verts (333 au
  total).

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
`scripts/calculer_statistiques.py`) : score neutre (50) si aucune statistique
ou échantillon `< 3` courses, sinon ROI normalisé sur `[-30 %, +30 %]`
(bornes assumées, clampées au-delà — aucune formule SAD pour ces bornes).
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
- `scripts/analyser_course.py` ne branche pas encore `ConsensusPresseService` (il
  construit `PreparationDonneesService` sans ce collaborateur optionnel) —
  uniquement `POST /courses/{id}/analyses/auto` en bénéficie pour l'instant.
- `Course.quinte` (colonne existante en base) n'est pas encore alimentée par le
  collecteur PMU (`CollecteService`) — non nécessaire au fonctionnement du
  consensus presse actuel, qui s'appuie sur le `R{réunion}C{course}` extrait de
  Canalturf lui-même, pas sur cette colonne.

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

- Automatisations planifiées (L017/L033) — aucun scheduler, `automations/` est un
  squelette vide. **Redimensionné volontairement (2026-07-09)** : pour un usage
  mono-utilisateur local, un vrai scheduler générique n'apporte rien — remplacé
  par de simples déclenchements manuels, désormais construits (page
  Administration de l'interface HTML, `POST /administration/automatisations/*`,
  cf. ci-dessous) plutôt qu'une planification récurrente configurable
  (régularité/heures) — pas de table de configuration de cron, pas de
  scheduler en tâche de fond dans le process API.
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

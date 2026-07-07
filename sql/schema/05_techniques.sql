-- Tables techniques (cf. L011 §10, L030.5) — fonctionnement interne, aucune donnée hippique.

CREATE TABLE IF NOT EXISTS role (
    id            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nom           VARCHAR(40) NOT NULL UNIQUE,
    description   TEXT,
    cree_le       TIMESTAMP NOT NULL DEFAULT now(),
    CONSTRAINT ck_role_nom CHECK (nom IN ('Administrateur', 'Analyste', 'Consultation', 'Automatisation'))
);

CREATE TABLE IF NOT EXISTS utilisateur (
    id                    BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    login                 VARCHAR(80) NOT NULL UNIQUE,
    mot_de_passe          VARCHAR(255) NOT NULL,
    nom                   VARCHAR(120),
    email                 VARCHAR(150),
    role_id               BIGINT NOT NULL REFERENCES role(id) ON DELETE RESTRICT,
    actif                 BOOLEAN NOT NULL DEFAULT TRUE,
    derniere_connexion    TIMESTAMP,
    cree_le               TIMESTAMP NOT NULL DEFAULT now(),
    modifie_le            TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_utilisateur_role ON utilisateur (role_id);

CREATE TABLE IF NOT EXISTS audit (
    id                BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    utilisateur_id    BIGINT REFERENCES utilisateur(id) ON DELETE RESTRICT,
    date_action       TIMESTAMP NOT NULL DEFAULT now(),
    action            VARCHAR(120) NOT NULL,
    objet             VARCHAR(120),
    ancien_etat       TEXT,
    nouvel_etat       TEXT
);
CREATE INDEX IF NOT EXISTS idx_audit_utilisateur ON audit (utilisateur_id);
CREATE INDEX IF NOT EXISTS idx_audit_date ON audit (date_action);

CREATE TABLE IF NOT EXISTS parametre (
    id                    BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    cle                   VARCHAR(120) NOT NULL UNIQUE,
    valeur                TEXT NOT NULL,
    type                  VARCHAR(20) NOT NULL DEFAULT 'String',
    description           TEXT,
    date_modification     TIMESTAMP NOT NULL DEFAULT now(),
    CONSTRAINT ck_parametre_type CHECK (type IN ('Integer', 'Decimal', 'Boolean', 'String'))
);

CREATE TABLE IF NOT EXISTS version (
    id                  BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    version             VARCHAR(20) NOT NULL UNIQUE,
    commit_git          VARCHAR(80),
    branche             VARCHAR(40),
    date_publication    TIMESTAMP NOT NULL DEFAULT now(),
    commentaire         TEXT
);

-- Table de suivi des migrations (cf. L013 §4) — une migration exécutée n'est jamais rejouée.
CREATE TABLE IF NOT EXISTS migration (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    version         VARCHAR(40) NOT NULL UNIQUE,
    fichier         VARCHAR(255) NOT NULL,
    checksum        VARCHAR(128) NOT NULL,
    debut           TIMESTAMP NOT NULL,
    fin             TIMESTAMP,
    duree_ms        INTEGER,
    resultat        VARCHAR(20) NOT NULL DEFAULT 'succes',
    CONSTRAINT ck_migration_resultat CHECK (resultat IN ('succes', 'echec'))
);

CREATE TABLE IF NOT EXISTS journal (
    id                BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    date_evenement    TIMESTAMP NOT NULL DEFAULT now(),
    niveau            VARCHAR(20) NOT NULL,
    composant         VARCHAR(60),
    correlation_id    VARCHAR(64),
    message           TEXT NOT NULL,
    exception         TEXT,
    CONSTRAINT ck_journal_niveau CHECK (niveau IN ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'))
);
CREATE INDEX IF NOT EXISTS idx_journal_date ON journal (date_evenement);
CREATE INDEX IF NOT EXISTS idx_journal_correlation ON journal (correlation_id);

CREATE TABLE IF NOT EXISTS tache (
    id             BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nom            VARCHAR(100) NOT NULL,
    categorie      VARCHAR(40),
    debut          TIMESTAMP NOT NULL DEFAULT now(),
    fin            TIMESTAMP,
    duree_ms       INTEGER,
    statut         VARCHAR(20) NOT NULL DEFAULT 'en_cours',
    commentaire    TEXT,
    CONSTRAINT ck_tache_statut CHECK (statut IN ('en_cours', 'succes', 'echec'))
);
CREATE INDEX IF NOT EXISTS idx_tache_nom ON tache (nom);

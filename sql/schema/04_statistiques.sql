-- Tables statistiques (cf. L011 §9, L030.4) — alimentées exclusivement par les traitements
-- automatiques ; aucune modification manuelle (cf. L030.4 §2).

CREATE TABLE IF NOT EXISTS statistique_globale (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    date_calcul     TIMESTAMP NOT NULL DEFAULT now(),
    nb_courses      INTEGER NOT NULL DEFAULT 0,
    nb_jouees       INTEGER NOT NULL DEFAULT 0,
    nb_ignorees     INTEGER NOT NULL DEFAULT 0,
    mises           DECIMAL(12,2) NOT NULL DEFAULT 0,
    gains           DECIMAL(12,2) NOT NULL DEFAULT 0,
    profit          DECIMAL(12,2),
    roi             DECIMAL(8,2),
    taux_reussite   DECIMAL(5,2),
    cree_le         TIMESTAMP NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_stat_global_date ON statistique_globale (date_calcul);

CREATE TABLE IF NOT EXISTS statistique_score (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    score_min       DECIMAL(5,2) NOT NULL,
    score_max       DECIMAL(5,2) NOT NULL,
    nb_courses      INTEGER NOT NULL DEFAULT 0,
    nb_gagnantes    INTEGER NOT NULL DEFAULT 0,
    roi             DECIMAL(8,2),
    taux_reussite   DECIMAL(5,2),
    cree_le         TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS statistique_hippodrome (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    hippodrome_id   BIGINT NOT NULL REFERENCES hippodrome(id) ON DELETE RESTRICT,
    nb_courses      INTEGER NOT NULL DEFAULT 0,
    mises           DECIMAL(12,2) NOT NULL DEFAULT 0,
    gains           DECIMAL(12,2) NOT NULL DEFAULT 0,
    profit          DECIMAL(12,2),
    roi             DECIMAL(8,2),
    cree_le         TIMESTAMP NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_stat_hippodrome ON statistique_hippodrome (hippodrome_id);

CREATE TABLE IF NOT EXISTS statistique_discipline (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    discipline_id   BIGINT NOT NULL REFERENCES discipline(id) ON DELETE RESTRICT,
    nb_courses      INTEGER NOT NULL DEFAULT 0,
    mises           DECIMAL(12,2) NOT NULL DEFAULT 0,
    gains           DECIMAL(12,2) NOT NULL DEFAULT 0,
    profit          DECIMAL(12,2),
    roi             DECIMAL(8,2),
    cree_le         TIMESTAMP NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_stat_discipline ON statistique_discipline (discipline_id);

CREATE TABLE IF NOT EXISTS statistique_pari (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    type_pari       VARCHAR(40) NOT NULL,
    nb_paris        INTEGER NOT NULL DEFAULT 0,
    mises           DECIMAL(12,2) NOT NULL DEFAULT 0,
    gains           DECIMAL(12,2) NOT NULL DEFAULT 0,
    profit          DECIMAL(12,2),
    roi             DECIMAL(8,2),
    taux_reussite   DECIMAL(5,2),
    cree_le         TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS statistique_modele (
    id               BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    version_modele   VARCHAR(60) NOT NULL,
    date_debut       DATE,
    date_fin         DATE,
    nb_courses       INTEGER NOT NULL DEFAULT 0,
    roi              DECIMAL(8,2),
    taux_reussite    DECIMAL(5,2),
    parametres       TEXT,
    commentaire      TEXT,
    cree_le          TIMESTAMP NOT NULL DEFAULT now()
);

-- Tables d'analyses (cf. L011 §8, L030.3) — immuables après création (cf. ADR-002 de L001).
-- Aucune colonne modifie_le : un recalcul crée une nouvelle version, jamais une mise à jour en place.

CREATE TABLE IF NOT EXISTS analyses (
    id                BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    course_id         BIGINT NOT NULL REFERENCES course(id) ON DELETE RESTRICT,
    version           SMALLINT NOT NULL,
    date_calcul       TIMESTAMP NOT NULL DEFAULT now(),
    score_confiance   DECIMAL(5,2),
    risque            DECIMAL(5,2),
    roi_theorique     DECIMAL(8,2),
    decision          VARCHAR(20),
    budget            DECIMAL(8,2) DEFAULT 0,
    commentaire       TEXT,
    cree_le           TIMESTAMP NOT NULL DEFAULT now(),
    CONSTRAINT uk_analyse_version UNIQUE (course_id, version),
    CONSTRAINT ck_analyse_score CHECK (score_confiance IS NULL OR (score_confiance >= 0 AND score_confiance <= 100)),
    CONSTRAINT ck_analyse_risque CHECK (risque IS NULL OR (risque >= 0 AND risque <= 100)),
    CONSTRAINT ck_analyse_budget CHECK (budget >= 0)
);
CREATE INDEX IF NOT EXISTS idx_analyse_course ON analyses (course_id);
CREATE INDEX IF NOT EXISTS idx_analyse_score ON analyses (score_confiance);
CREATE INDEX IF NOT EXISTS idx_analyse_date ON analyses (date_calcul);

CREATE TABLE IF NOT EXISTS analyse_partant (
    id               BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    analyse_id       BIGINT NOT NULL REFERENCES analyses(id) ON DELETE CASCADE,
    partant_id       BIGINT NOT NULL REFERENCES partant(id) ON DELETE RESTRICT,
    score            DECIMAL(6,2),
    rang             SMALLINT,
    consensus        DECIMAL(5,2),
    evolution_cote   DECIMAL(6,2),
    value_bet        BOOLEAN NOT NULL DEFAULT FALSE,
    confiance        DECIMAL(5,2),
    commentaire      TEXT,
    cree_le          TIMESTAMP NOT NULL DEFAULT now(),
    CONSTRAINT uk_analyse_partant UNIQUE (analyse_id, partant_id)
);
CREATE INDEX IF NOT EXISTS idx_analyse_partant_analyse ON analyse_partant (analyse_id);
CREATE INDEX IF NOT EXISTS idx_analyse_partant_partant ON analyse_partant (partant_id);

CREATE TABLE IF NOT EXISTS selection (
    id                BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    analyse_id        BIGINT NOT NULL REFERENCES analyses(id) ON DELETE CASCADE,
    partant_id        BIGINT NOT NULL REFERENCES partant(id) ON DELETE RESTRICT,
    categorie         VARCHAR(30) NOT NULL,
    ordre_affichage   SMALLINT,
    cree_le           TIMESTAMP NOT NULL DEFAULT now(),
    CONSTRAINT ck_selection_categorie CHECK (categorie IN ('Base', 'Chance régulière', 'Outsider', 'Tocard', 'Écarté'))
);
CREATE INDEX IF NOT EXISTS idx_selection_analyse ON selection (analyse_id);

CREATE TABLE IF NOT EXISTS pari (
    id             BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    analyse_id     BIGINT NOT NULL REFERENCES analyses(id) ON DELETE CASCADE,
    type_pari      VARCHAR(40) NOT NULL,
    combinaison    VARCHAR(255),
    mise           DECIMAL(8,2) NOT NULL DEFAULT 0,
    gain_estime    DECIMAL(10,2),
    roi_estime     DECIMAL(8,2),
    cree_le        TIMESTAMP NOT NULL DEFAULT now(),
    CONSTRAINT ck_pari_mise CHECK (mise >= 0)
);
CREATE INDEX IF NOT EXISTS idx_pari_analyse ON pari (analyse_id);

CREATE TABLE IF NOT EXISTS controle_roi (
    id             BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    analyse_id     BIGINT NOT NULL REFERENCES analyses(id) ON DELETE RESTRICT,
    mise           DECIMAL(8,2) NOT NULL DEFAULT 0,
    gains          DECIMAL(10,2) NOT NULL DEFAULT 0,
    profit         DECIMAL(10,2),
    roi            DECIMAL(8,2),
    valide         BOOLEAN NOT NULL DEFAULT FALSE,
    commentaire    TEXT,
    cree_le        TIMESTAMP NOT NULL DEFAULT now(),
    CONSTRAINT uk_controle_roi_analyse UNIQUE (analyse_id),
    CONSTRAINT ck_controle_roi_mise CHECK (mise >= 0),
    CONSTRAINT ck_controle_roi_gains CHECK (gains >= 0)
);

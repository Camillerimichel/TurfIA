-- Tables métier (cf. L011 §7, L030.2) — données quotidiennes exploitées par TurfIA.

CREATE TABLE IF NOT EXISTS reunion (
    id             BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    date           DATE NOT NULL,
    hippodrome_id  BIGINT NOT NULL REFERENCES hippodrome(id) ON DELETE RESTRICT,
    numero         SMALLINT NOT NULL,
    heure_debut    TIMESTAMP,
    heure_fin      TIMESTAMP,
    statut         VARCHAR(20) NOT NULL DEFAULT 'Prévue',
    cree_le        TIMESTAMP NOT NULL DEFAULT now(),
    modifie_le     TIMESTAMP,
    CONSTRAINT uk_reunion UNIQUE (date, hippodrome_id, numero),
    CONSTRAINT ck_reunion_statut CHECK (statut IN ('Prévue', 'En cours', 'Terminée', 'Annulée'))
);
CREATE INDEX IF NOT EXISTS idx_reunion_date ON reunion (date);
CREATE INDEX IF NOT EXISTS idx_reunion_hippodrome ON reunion (hippodrome_id);

CREATE TABLE IF NOT EXISTS course (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    reunion_id      BIGINT NOT NULL REFERENCES reunion(id) ON DELETE RESTRICT,
    numero          SMALLINT NOT NULL,
    nom             VARCHAR(150) NOT NULL,
    heure_depart    TIMESTAMP,
    discipline_id   BIGINT REFERENCES discipline(id) ON DELETE RESTRICT,
    type_course_id  BIGINT REFERENCES type_course(id) ON DELETE RESTRICT,
    distance_id     BIGINT REFERENCES distance(id) ON DELETE RESTRICT,
    surface_id      BIGINT REFERENCES surface(id) ON DELETE RESTRICT,
    etat_piste_id   BIGINT REFERENCES etat_piste(id) ON DELETE RESTRICT,
    allocation      DECIMAL(12,2),
    nb_partants     SMALLINT,
    quinte          BOOLEAN NOT NULL DEFAULT FALSE,
    cree_le         TIMESTAMP NOT NULL DEFAULT now(),
    modifie_le      TIMESTAMP,
    CONSTRAINT uk_course UNIQUE (reunion_id, numero)
);
CREATE INDEX IF NOT EXISTS idx_course_reunion ON course (reunion_id);
CREATE INDEX IF NOT EXISTS idx_course_heure_depart ON course (heure_depart);
CREATE INDEX IF NOT EXISTS idx_course_discipline ON course (discipline_id);
CREATE INDEX IF NOT EXISTS idx_course_distance ON course (distance_id);

CREATE TABLE IF NOT EXISTS cheval (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nom             VARCHAR(120) NOT NULL,
    sexe            CHAR(1) CHECK (sexe IN ('M', 'F', 'H')),
    date_naissance  DATE,
    pere            VARCHAR(120),
    mere            VARCHAR(120),
    gains           DECIMAL(14,2) NOT NULL DEFAULT 0,
    musique         VARCHAR(100),
    actif           BOOLEAN NOT NULL DEFAULT TRUE,
    cree_le         TIMESTAMP NOT NULL DEFAULT now(),
    modifie_le      TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_cheval_nom ON cheval (nom);

CREATE TABLE IF NOT EXISTS jockey (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nom         VARCHAR(120) NOT NULL,
    prenom      VARCHAR(80),
    licence     VARCHAR(40),
    actif       BOOLEAN NOT NULL DEFAULT TRUE,
    cree_le     TIMESTAMP NOT NULL DEFAULT now(),
    modifie_le  TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_jockey_nom ON jockey (nom);

CREATE TABLE IF NOT EXISTS entraineur (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nom         VARCHAR(120) NOT NULL,
    prenom      VARCHAR(80),
    actif       BOOLEAN NOT NULL DEFAULT TRUE,
    cree_le     TIMESTAMP NOT NULL DEFAULT now(),
    modifie_le  TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_entraineur_nom ON entraineur (nom);

CREATE TABLE IF NOT EXISTS partant (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    course_id       BIGINT NOT NULL REFERENCES course(id) ON DELETE RESTRICT,
    cheval_id       BIGINT NOT NULL REFERENCES cheval(id) ON DELETE RESTRICT,
    jockey_id       BIGINT REFERENCES jockey(id) ON DELETE RESTRICT,
    entraineur_id   BIGINT REFERENCES entraineur(id) ON DELETE RESTRICT,
    numero          SMALLINT NOT NULL,
    corde           SMALLINT,
    poids           DECIMAL(5,1),
    valeur          DECIMAL(5,2),
    age             SMALLINT,
    ferrure         VARCHAR(30),
    musique         VARCHAR(80),
    non_partant     BOOLEAN NOT NULL DEFAULT FALSE,
    cree_le         TIMESTAMP NOT NULL DEFAULT now(),
    modifie_le      TIMESTAMP,
    CONSTRAINT uk_partant_numero UNIQUE (course_id, numero),
    CONSTRAINT uk_partant_cheval UNIQUE (course_id, cheval_id),
    CONSTRAINT ck_partant_numero CHECK (numero > 0)
);
CREATE INDEX IF NOT EXISTS idx_partant_course ON partant (course_id);
CREATE INDEX IF NOT EXISTS idx_partant_cheval ON partant (cheval_id);
CREATE INDEX IF NOT EXISTS idx_partant_jockey ON partant (jockey_id);
CREATE INDEX IF NOT EXISTS idx_partant_entraineur ON partant (entraineur_id);

-- Historique des cotes : jamais remplacée, toujours un nouvel enregistrement (cf. L011 §15).
CREATE TABLE IF NOT EXISTS cote (
    id           BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    partant_id   BIGINT NOT NULL REFERENCES partant(id) ON DELETE RESTRICT,
    operateur    VARCHAR(40) NOT NULL,
    cote         DECIMAL(6,2) NOT NULL,
    evolution    DECIMAL(6,2),
    date_maj     TIMESTAMP NOT NULL DEFAULT now(),
    cree_le      TIMESTAMP NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_cote_partant ON cote (partant_id);
CREATE INDEX IF NOT EXISTS idx_cote_date ON cote (partant_id, date_maj);

-- Résultats officiels : figés après validation (cf. L009 §5.1 registre des règles, règle RG-CONTROLE-001).
CREATE TABLE IF NOT EXISTS resultat (
    id                BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    course_id         BIGINT NOT NULL REFERENCES course(id) ON DELETE RESTRICT,
    partant_id        BIGINT NOT NULL REFERENCES partant(id) ON DELETE RESTRICT,
    classement        SMALLINT,
    temps             VARCHAR(20),
    ecart             VARCHAR(30),
    disqualification  BOOLEAN NOT NULL DEFAULT FALSE,
    non_partant       BOOLEAN NOT NULL DEFAULT FALSE,
    cree_le           TIMESTAMP NOT NULL DEFAULT now(),
    CONSTRAINT uk_resultat_classement UNIQUE (course_id, classement),
    CONSTRAINT ck_resultat_classement CHECK (classement IS NULL OR classement > 0)
);
CREATE INDEX IF NOT EXISTS idx_resultat_course ON resultat (course_id);

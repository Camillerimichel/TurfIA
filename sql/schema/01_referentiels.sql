-- Tables de référence (cf. L011 §6, L030.1) — données stables, alimentées par la collecte.
-- Suppression physique interdite (cf. L011 §8.1, désactivation logique via `actif`).

CREATE TABLE IF NOT EXISTS corde (
    id            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    libelle       VARCHAR(40) NOT NULL UNIQUE,
    cree_le       TIMESTAMP NOT NULL DEFAULT now(),
    modifie_le    TIMESTAMP
);

CREATE TABLE IF NOT EXISTS hippodrome (
    id            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nom           VARCHAR(100) NOT NULL,
    ville         VARCHAR(80),
    pays          VARCHAR(50),
    corde_id      BIGINT REFERENCES corde(id) ON DELETE RESTRICT,
    altitude      INTEGER,
    latitude      DECIMAL(9,6),
    longitude     DECIMAL(9,6),
    cree_le       TIMESTAMP NOT NULL DEFAULT now(),
    modifie_le    TIMESTAMP,
    CONSTRAINT uk_hippodrome_nom UNIQUE (nom)
);
CREATE INDEX IF NOT EXISTS idx_hippodrome_nom ON hippodrome (nom);

CREATE TABLE IF NOT EXISTS discipline (
    id            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    libelle       VARCHAR(40) NOT NULL UNIQUE,
    description   TEXT,
    cree_le       TIMESTAMP NOT NULL DEFAULT now(),
    modifie_le    TIMESTAMP
);

CREATE TABLE IF NOT EXISTS surface (
    id            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    libelle       VARCHAR(40) NOT NULL UNIQUE,
    description   TEXT,
    cree_le       TIMESTAMP NOT NULL DEFAULT now(),
    modifie_le    TIMESTAMP
);

CREATE TABLE IF NOT EXISTS etat_piste (
    id            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    libelle       VARCHAR(50) NOT NULL UNIQUE,
    indice        DECIMAL(4,2),
    cree_le       TIMESTAMP NOT NULL DEFAULT now(),
    modifie_le    TIMESTAMP
);

CREATE TABLE IF NOT EXISTS type_course (
    id            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    libelle       VARCHAR(80) NOT NULL UNIQUE,
    description   TEXT,
    cree_le       TIMESTAMP NOT NULL DEFAULT now(),
    modifie_le    TIMESTAMP
);

CREATE TABLE IF NOT EXISTS distance (
    id            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    distance      INTEGER NOT NULL,
    unite         VARCHAR(10) NOT NULL DEFAULT 'm',
    cree_le       TIMESTAMP NOT NULL DEFAULT now(),
    CONSTRAINT uk_distance UNIQUE (distance, unite)
);

CREATE TABLE IF NOT EXISTS meteo (
    id             BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    temperature    DECIMAL(4,1),
    vent           DECIMAL(5,1),
    precipitation  DECIMAL(5,1),
    commentaire    TEXT,
    cree_le        TIMESTAMP NOT NULL DEFAULT now()
);

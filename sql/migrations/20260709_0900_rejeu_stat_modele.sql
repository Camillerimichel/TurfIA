-- Étend `statistique_modele` pour le moteur de rejeu/backtesting (L031.7 §4,
-- cf. scripts/rejouer_versions.py) : `version_modele` élargi (VARCHAR(20) était
-- trop court pour un identifiant descriptif) et nouvelle colonne `parametres`
-- (JSON des poids_score/poids_risque effectivement testés, traçabilité L031.7
-- §7/§9). CREATE TABLE IF NOT EXISTS (cf. schema/04_statistiques.sql, déjà
-- réinclus ci-dessous) ne modifie pas une table déjà existante : les ALTER
-- explicites ci-dessous sont donc nécessaires, et idempotents (ADD COLUMN IF
-- NOT EXISTS ; ALTER COLUMN TYPE vers un type plus large est un no-op si déjà
-- appliqué).

ALTER TABLE statistique_modele ALTER COLUMN version_modele TYPE VARCHAR(60);
ALTER TABLE statistique_modele ADD COLUMN IF NOT EXISTS parametres TEXT;

-- INCLUDE: ../schema/04_statistiques.sql

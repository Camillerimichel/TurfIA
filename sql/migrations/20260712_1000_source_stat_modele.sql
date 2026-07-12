-- Distingue les deux mécanismes qui alimentent `statistique_modele` (retour
-- utilisateur, 2026-07-12 : « on ne sait pas à quoi correspondent les
-- différentes versions ») : "automatique" (StatistiqueRepository.
-- calculer_modeles, agrégation Pré/Finale par analyses.version, PAS un vrai
-- jeu de poids différent) et "rejeu" (scripts/rejouer_versions.py, vrai
-- backtest à poids différents). `CREATE TABLE IF NOT EXISTS` (cf.
-- schema/04_statistiques.sql, réinclus ci-dessous) ne modifie pas une table
-- déjà existante : l'ADD COLUMN explicite ci-dessous est donc nécessaire, et
-- idempotent. Toutes les lignes déjà en base viennent de la voie
-- automatique (vérifié réellement le 2026-07-12 : aucun rejeu manuel n'avait
-- encore été exécuté) — le défaut 'automatique' est donc correct pour elles.

ALTER TABLE statistique_modele ADD COLUMN IF NOT EXISTS source VARCHAR(20) NOT NULL DEFAULT 'automatique';
ALTER TABLE statistique_modele DROP CONSTRAINT IF EXISTS ck_statistique_modele_source;
ALTER TABLE statistique_modele ADD CONSTRAINT ck_statistique_modele_source CHECK (source IN ('automatique', 'rejeu'));

-- INCLUDE: ../schema/04_statistiques.sql

-- Ajoute les indicateurs L031.7 §5 manquants au moteur de rejeu (ROI par
-- tranche de score/hippodrome/type de pari, drawdown, stabilité) — cf.
-- scripts/rejouer_versions.py, src/algorithms/rejeu.py. `CREATE TABLE IF NOT
-- EXISTS` (cf. schema/04_statistiques.sql, réinclus ci-dessous) ne modifie pas
-- une table déjà existante : les ADD COLUMN explicites ci-dessous sont donc
-- nécessaires, et idempotents.

ALTER TABLE statistique_modele ADD COLUMN IF NOT EXISTS roi_par_score TEXT;
ALTER TABLE statistique_modele ADD COLUMN IF NOT EXISTS roi_par_hippodrome TEXT;
ALTER TABLE statistique_modele ADD COLUMN IF NOT EXISTS roi_par_type_pari TEXT;
ALTER TABLE statistique_modele ADD COLUMN IF NOT EXISTS drawdown DECIMAL(8,2);
ALTER TABLE statistique_modele ADD COLUMN IF NOT EXISTS stabilite DECIMAL(8,2);

-- INCLUDE: ../schema/04_statistiques.sql

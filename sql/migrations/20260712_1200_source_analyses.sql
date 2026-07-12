-- Distingue une analyse issue du formulaire classique ('manuel') d'une
-- analyse IA à la demande via l'API Claude ('ia', cf. IaAnalyseService) —
-- même principe que la migration 20260712_1000_source_stat_modele.sql pour
-- statistique_modele. `CREATE TABLE IF NOT EXISTS` (cf. schema/03_analyses.sql,
-- réinclus ci-dessous) ne modifie pas la table `analyses` déjà existante :
-- l'ADD COLUMN explicite ci-dessous est donc nécessaire, et idempotent.
-- Toutes les lignes déjà en base viennent du formulaire manuel (aucune
-- analyse IA n'a encore jamais été calculée) — le défaut 'manuel' est donc
-- correct pour elles.

ALTER TABLE analyses ADD COLUMN IF NOT EXISTS source VARCHAR(20) NOT NULL DEFAULT 'manuel';
ALTER TABLE analyses DROP CONSTRAINT IF EXISTS ck_analyse_source;
ALTER TABLE analyses ADD CONSTRAINT ck_analyse_source CHECK (source IN ('manuel', 'ia'));

-- INCLUDE: ../schema/03_analyses.sql
-- INCLUDE: ../schema/06_grants.sql

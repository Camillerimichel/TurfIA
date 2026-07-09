-- Étend les droits de turfia_app à `version` (oubliée du GRANT initial, cf.
-- sql/schema/06_grants.sql) — nécessaire pour GET /administration/versions
-- (L018 §10 « consulter les versions ») et scripts/publier_version.py.
--
-- Ré-inclut le fichier entier plutôt que juste le delta : GRANT déjà accordé
-- est un no-op, cf. L013 §7 (pas de duplication du DDL), même pratique que
-- 20260708_0918_ajout_session_et_grants.sql.

-- INCLUDE: ../schema/06_grants.sql

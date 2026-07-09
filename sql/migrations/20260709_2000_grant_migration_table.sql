-- `pg_dump` exécuté avec turfia_app (cf. scripts/sauvegarder_base.py, L018 §10
-- « vérifier les sauvegardes ») doit pouvoir verrouiller/lire TOUTES les tables
-- du schéma, `migration` y compris, sinon il échoue avec "permission denied
-- for table migration". SELECT seule (jamais INSERT/UPDATE, réservé à
-- turfia_migration) — cf. sql/schema/06_grants.sql, réinclus ci-dessous.

-- INCLUDE: ../schema/06_grants.sql

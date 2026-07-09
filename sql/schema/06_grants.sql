-- Droits d'accès par rôle applicatif (cf. L011 §16.5, L012 §2.3).
-- turfia_app : lecture/écriture sur métier et analyses. turfia_readonly : lecture seule partout.

GRANT USAGE ON SCHEMA public TO turfia_app, turfia_readonly;

GRANT SELECT, INSERT, UPDATE ON
    corde, hippodrome, discipline, surface, etat_piste, type_course, distance, meteo,
    reunion, course, cheval, jockey, entraineur, partant, cote, resultat,
    analyses, analyse_partant, selection, pari, controle_roi, controle_roi_pari,
    statistique_globale, statistique_score, statistique_hippodrome, statistique_discipline,
    statistique_pari, statistique_modele,
    parametre, tache, journal, version,
    role, utilisateur, session, audit
TO turfia_app;

-- SELECT seule (jamais INSERT/UPDATE, réservé à turfia_migration) : nécessaire
-- pour que `pg_dump` exécuté avec turfia_app (cf. scripts/sauvegarder_base.py,
-- L018 §10 « vérifier les sauvegardes ») puisse verrouiller/lire TOUTES les
-- tables du schéma, `migration` y compris (sinon `pg_dump` échoue avec
-- "permission denied for table migration").
GRANT SELECT ON migration TO turfia_app;

GRANT SELECT ON ALL TABLES IN SCHEMA public TO turfia_readonly;

GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO turfia_app;

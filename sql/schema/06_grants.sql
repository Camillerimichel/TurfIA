-- Droits d'accès par rôle applicatif (cf. L011 §16.5, L012 §2.3).
-- turfia_app : lecture/écriture sur métier et analyses. turfia_readonly : lecture seule partout.

GRANT USAGE ON SCHEMA public TO turfia_app, turfia_readonly;

GRANT SELECT, INSERT, UPDATE ON
    corde, hippodrome, discipline, surface, etat_piste, type_course, distance, meteo,
    reunion, course, cheval, jockey, entraineur, partant, cote, resultat,
    analyse, analyse_partant, selection, pari, controle_roi,
    statistique_globale, statistique_score, statistique_hippodrome, statistique_discipline,
    statistique_pari, statistique_modele,
    parametre, tache, journal
TO turfia_app;

GRANT SELECT ON ALL TABLES IN SCHEMA public TO turfia_readonly;

GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO turfia_app;

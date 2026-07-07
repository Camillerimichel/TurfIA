-- Données de référence minimales (cf. L030.1) — idempotent grâce à ON CONFLICT.

INSERT INTO corde (libelle) VALUES ('Gauche'), ('Droite')
ON CONFLICT (libelle) DO NOTHING;

INSERT INTO discipline (libelle) VALUES
    ('Plat'), ('Trot Attelé'), ('Trot Monté'), ('Haies'), ('Steeple'), ('Cross')
ON CONFLICT (libelle) DO NOTHING;

INSERT INTO surface (libelle) VALUES
    ('Gazon'), ('PSF'), ('Cendrée'), ('Sable fibré')
ON CONFLICT (libelle) DO NOTHING;

INSERT INTO etat_piste (libelle, indice) VALUES
    ('Très souple', 1.0), ('Souple', 2.0), ('Bon', 3.0), ('Lourd', 4.0)
ON CONFLICT (libelle) DO NOTHING;

INSERT INTO type_course (libelle) VALUES
    ('Handicap'), ('Groupe I'), ('Groupe II'), ('Groupe III'), ('Listed'), ('Réclamer'), ('Maiden')
ON CONFLICT (libelle) DO NOTHING;

INSERT INTO role (nom, description) VALUES
    ('Administrateur', 'Gestion complète'),
    ('Analyste', 'Analyses et statistiques'),
    ('Consultation', 'Lecture seule'),
    ('Automatisation', 'Services internes')
ON CONFLICT (nom) DO NOTHING;

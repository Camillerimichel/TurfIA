-- Rôles applicatifs (cf. L011 §16.5) — principe du moindre privilège.
-- Les mots de passe réels sont fournis par l'exploitation (cf. L021, L026), jamais en clair ici.

DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'turfia_app') THEN
        CREATE ROLE turfia_app LOGIN PASSWORD 'changeme';
    END IF;
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'turfia_readonly') THEN
        CREATE ROLE turfia_readonly LOGIN PASSWORD 'changeme';
    END IF;
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'turfia_migration') THEN
        CREATE ROLE turfia_migration LOGIN PASSWORD 'changeme' CREATEDB;
    END IF;
END
$$;

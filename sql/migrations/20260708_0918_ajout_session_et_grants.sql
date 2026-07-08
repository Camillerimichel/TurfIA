-- Ajoute la table `session` (authentification réelle, cf. L021 §3.3) et étend les
-- droits de turfia_app à role/utilisateur/session/audit (auparavant absents des
-- GRANTs, cf. L011 §16.5, L021 §2.3 moindre privilège).
--
-- Ré-inclut les fichiers entiers plutôt que juste le delta : toutes les
-- instructions sont idempotentes (CREATE TABLE/INDEX IF NOT EXISTS, GRANT déjà
-- accordé = no-op), cf. L013 §7 (pas de duplication du DDL).

-- INCLUDE: ../schema/05_techniques.sql
-- INCLUDE: ../schema/06_grants.sql

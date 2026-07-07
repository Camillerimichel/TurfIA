"""Runner de migrations SQL — cf. L013.

Exécute les fichiers de sql/migrations/ dans l'ordre chronologique (nommage
YYYYMMDD_HHMM_description.sql, cf. L013 §2.2), une seule fois chacun (cf. L013 §3.3),
dans une transaction (cf. L013 §6), en enregistrant le résultat dans la table `migration`
(cf. L013 §4.2).

Une ligne « -- INCLUDE: <chemin relatif> » est résolue en insérant le contenu du fichier
référencé (cf. sql/migrations/20260701_0900_creation_schema_initial.sql), afin que
sql/schema/ reste l'unique source de vérité du DDL (pas de duplication, cf. L013 §7).
"""

import hashlib
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import psycopg
from dotenv import load_dotenv

MIGRATIONS_DIR = Path(__file__).resolve().parent.parent / "sql" / "migrations"
INCLUDE_PREFIX = "-- INCLUDE:"

# Bootstrap minimal : la table de suivi doit exister avant même la première migration.
# Le DDL canonique et complet de `migration` reste sql/schema/05_techniques.sql (IF NOT
# EXISTS partagé, donc pas de conflit lorsque la migration initiale la recrée).
BOOTSTRAP_MIGRATION_TABLE = """
CREATE TABLE IF NOT EXISTS migration (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    version VARCHAR(40) NOT NULL UNIQUE,
    fichier VARCHAR(255) NOT NULL,
    checksum VARCHAR(128) NOT NULL,
    debut TIMESTAMP NOT NULL,
    fin TIMESTAMP,
    duree_ms INTEGER,
    resultat VARCHAR(20) NOT NULL DEFAULT 'succes'
);
"""


def resolve_includes(sql_file: Path) -> str:
    """Remplace les directives INCLUDE par le contenu des fichiers référencés."""
    resolved_parts = []
    for line in sql_file.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith(INCLUDE_PREFIX):
            included_path = (sql_file.parent / stripped[len(INCLUDE_PREFIX):].strip()).resolve()
            resolved_parts.append(included_path.read_text(encoding="utf-8"))
        else:
            resolved_parts.append(line)
    return "\n".join(resolved_parts)


def already_applied(conn: psycopg.Connection) -> set[str]:
    with conn.cursor() as cur:
        cur.execute("SELECT version FROM migration")
        return {row[0] for row in cur.fetchall()}


def apply_migration(conn: psycopg.Connection, sql_file: Path, resolved_sql: str) -> None:
    version = sql_file.stem
    checksum = hashlib.sha256(resolved_sql.encode("utf-8")).hexdigest()
    debut = datetime.now(timezone.utc)
    start = time.monotonic()

    try:
        with conn.transaction():
            with conn.cursor() as cur:
                cur.execute(resolved_sql)
        resultat = "succes"
    except Exception:
        resultat = "echec"
        raise
    finally:
        duree_ms = int((time.monotonic() - start) * 1000)
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO migration (version, fichier, checksum, debut, fin, duree_ms, resultat)
                VALUES (%s, %s, %s, %s, now(), %s, %s)
                """,
                (version, sql_file.name, checksum, debut, duree_ms, resultat),
            )
        conn.commit()


def run() -> int:
    load_dotenv()
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("DATABASE_URL manquant (cf. L026) — arrêt.", file=sys.stderr)
        return 1

    migration_files = sorted(MIGRATIONS_DIR.glob("*.sql"))
    if not migration_files:
        print("Aucun fichier de migration trouvé.")
        return 0

    with psycopg.connect(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute(BOOTSTRAP_MIGRATION_TABLE)
        conn.commit()

        applied = already_applied(conn)

        for sql_file in migration_files:
            version = sql_file.stem
            if version in applied:
                print(f"[SKIP] {version} (déjà appliquée)")
                continue

            resolved_sql = resolve_includes(sql_file)
            print(f"[RUN]  {version}")
            apply_migration(conn, sql_file, resolved_sql)
            print(f"[OK]   {version}")

    return 0


if __name__ == "__main__":
    sys.exit(run())

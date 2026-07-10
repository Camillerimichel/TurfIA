"""Point d'entrée de l'API REST TurfIA — cf. L007, L016, L032.1.

Démarrage fail-fast : `get_settings()` lève ConfigurationError si la configuration est
incomplète (cf. L026 §2.3), avant même que l'application ne commence à servir des
requêtes.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from api.middlewares.error_handler import register_error_handlers
from api.routes import (
    administration,
    analyses,
    audit,
    auth,
    courses,
    historique,
    referentiels,
    statistiques,
    system,
)
from src.core.config import get_settings
from src.core.log_db_handler import DbLogHandler
from src.core.logging import configure_logging

RACINE_PROJET = Path(__file__).resolve().parent.parent


class StaticFilesSansCache(StaticFiles):
    """`Cache-Control: no-cache` sur chaque réponse — force le navigateur à
    revalider (ETag/Last-Modified, déjà gérés nativement par Starlette) avant
    de réutiliser une copie en cache, plutôt que de suivre une politique
    heuristique qui peut servir un fichier JS/CSS périmé après une
    modification (rencontré réellement en test manuel de l'interface HTML,
    cf. PROJECT_STATE.md) — sans dépendance ajoutée, coût négligeable vu la
    taille des fichiers et l'usage strictement local."""

    def file_response(self, *args, **kwargs):
        response = super().file_response(*args, **kwargs)
        response.headers["Cache-Control"] = "no-cache"
        return response

settings = get_settings()
configure_logging(settings.log_level)

# Persiste les logs WARNING+ dans la table `journal` (cf. L022, L018 §10) — en
# plus du flux stdout JSON existant, jamais à sa place. Désactivable
# (LOG_JOURNAL_DB_ACTIF=false) pour les tests, qui n'ont pas de base réelle.
if os.environ.get("LOG_JOURNAL_DB_ACTIF", "true").lower() != "false":
    logging.getLogger().addHandler(DbLogHandler(settings.database_url, niveau=settings.log_niveau_db))

app = FastAPI(
    title="TurfIA API",
    version="0.1.0",
    openapi_url=f"{settings.api_prefix}/openapi.json",
    docs_url=f"{settings.api_prefix}/docs",
)

register_error_handlers(app)

app.include_router(system.router, prefix=settings.api_prefix)
app.include_router(auth.router, prefix=settings.api_prefix)
app.include_router(referentiels.router, prefix=settings.api_prefix)
app.include_router(courses.router, prefix=settings.api_prefix)
app.include_router(analyses.router, prefix=settings.api_prefix)
app.include_router(statistiques.router, prefix=settings.api_prefix)
app.include_router(audit.router, prefix=settings.api_prefix)
app.include_router(historique.router, prefix=settings.api_prefix)
app.include_router(administration.router, prefix=settings.api_prefix)

# Interface HTML locale (cf. L018) — montée après les routeurs API pour que
# `/api/v1/*` reste prioritaire. Pas de moteur de gabarits (Jinja2) : tout le
# contenu dynamique vient du JS via fetch() (cf. L018 §3.3, html/static/js/api.js).
app.mount("/static", StaticFilesSansCache(directory=RACINE_PROJET / "html" / "static"), name="static")
app.mount("/", StaticFilesSansCache(directory=RACINE_PROJET / "html" / "templates", html=True), name="html")

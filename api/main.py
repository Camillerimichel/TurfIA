"""Point d'entrée de l'API REST TurfIA — cf. L007, L016, L032.1.

Démarrage fail-fast : `get_settings()` lève ConfigurationError si la configuration est
incomplète (cf. L026 §2.3), avant même que l'application ne commence à servir des
requêtes.
"""

from __future__ import annotations

from fastapi import FastAPI

from api.middlewares.error_handler import register_error_handlers
from api.routes import analyses, auth, courses, referentiels, statistiques, system
from src.core.config import get_settings
from src.core.logging import configure_logging

settings = get_settings()
configure_logging(settings.log_level)

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

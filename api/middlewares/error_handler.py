"""Gestionnaire d'erreurs centralisé — cf. L032.1 §6, L023 §4.1, L016 §7.

Traduit la hiérarchie d'exceptions applicatives en réponses HTTP normalisées. Aucune
information technique interne (trace, message SQL) n'est jamais renvoyée au client :
seuls les messages des erreurs 4xx (déjà rédigés en langage métier) sont exposés.
"""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.core.exceptions import (
    ApplicationError,
    BusinessRuleError,
    ConfigurationError,
    DatabaseError,
    SecurityError,
    ValidationError,
)
from src.core.logging import get_logger

logger = get_logger("api.errors")

# Correspondance exception -> (code HTTP, code fonctionnel) — cf. L023 §4.1.
_CODE_MAP: dict[type[ApplicationError], tuple[int, str]] = {
    ValidationError: (422, "VALIDATION_ERROR"),
    SecurityError: (403, "SECURITY_ERROR"),
    BusinessRuleError: (409, "BUSINESS_RULE_ERROR"),
    DatabaseError: (500, "DATABASE_ERROR"),
    ConfigurationError: (500, "CONFIGURATION_ERROR"),
}


def _envelope(code: str, message: str) -> dict:
    return {"success": False, "error": {"code": code, "message": message}}


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(ApplicationError)
    async def handle_application_error(request: Request, exc: ApplicationError) -> JSONResponse:
        status_code, code = _CODE_MAP.get(type(exc), (500, "INTERNAL_ERROR"))
        logger.error(
            "Erreur applicative",
            exc_info=exc,
            extra={"context": {"code": code, "chemin": str(request.url)}},
        )
        message = str(exc) if status_code < 500 else "Une erreur interne est survenue."
        return JSONResponse(status_code=status_code, content=_envelope(code, message))

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        logger.error("Erreur non gérée", exc_info=exc, extra={"context": {"chemin": str(request.url)}})
        return JSONResponse(status_code=500, content=_envelope("INTERNAL_ERROR", "Une erreur interne est survenue."))

"""Journalisation structurée — cf. L022 §2.4 (format JSON), L022 §11 (confidentialité).

Chaque entrée comporte au minimum date, niveau, composant et message (cf. L022 §4).
Aucun champ sensible (mot de passe, secret, jeton) ne doit être passé en `extra`.
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone

_CONFIGURED = False

_SENSITIVE_KEYS = {"password", "mot_de_passe", "secret", "secret_key", "token", "jeton"}


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "date": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "niveau": record.levelname,
            "composant": record.name,
            "message": record.getMessage(),
        }
        correlation_id = getattr(record, "correlation_id", None)
        if correlation_id:
            payload["identifiant_correlation"] = correlation_id
        for key, value in getattr(record, "context", {}).items():
            if key.lower() not in _SENSITIVE_KEYS:
                payload[key] = value
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False, default=str)


def configure_logging(level: str = "INFO") -> None:
    """Configure la journalisation applicative (idempotent)."""
    global _CONFIGURED
    if _CONFIGURED:
        return

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())

    root = logging.getLogger()
    root.setLevel(level.upper())
    root.handlers = [handler]

    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)

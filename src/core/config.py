"""Chargement de la configuration — cf. L026.

Sépare configuration applicative non sensible (config/config.yaml, cf. L026 §3.2) et
secrets (variables d'environnement / .env, cf. L026 §4). Échoue au démarrage si la
configuration est incomplète (fail-fast, cf. L026 §2.3, ADR-001 de L010) plutôt que de
démarrer avec un comportement dégradé silencieux.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import yaml
from dotenv import load_dotenv

from src.core.exceptions import ConfigurationError

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent.parent / "config" / "config.yaml"


@dataclass(frozen=True)
class Settings:
    app_env: str
    app_port: int
    log_level: str
    database_url: str
    secret_key: str
    api_prefix: str
    pagination_default_size: int
    pagination_max_size: int
    session_duree_minutes: int
    login_max_tentatives: int
    login_fenetre_secondes: int


def load_settings(config_path: Path | None = None, load_env_file: bool = True) -> Settings:
    """Construit les Settings à partir de config/config.yaml + variables d'environnement.

    Lève ConfigurationError si une valeur requise est absente — ne retourne jamais un
    objet Settings partiellement valide.
    """
    if load_env_file:
        load_dotenv()

    path = config_path or DEFAULT_CONFIG_PATH
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except FileNotFoundError as exc:
        raise ConfigurationError(f"Fichier de configuration introuvable : {path}") from exc
    except yaml.YAMLError as exc:
        raise ConfigurationError(f"Fichier de configuration invalide : {path}") from exc

    database_url = os.environ.get("DATABASE_URL")
    secret_key = os.environ.get("SECRET_KEY")
    if not database_url:
        raise ConfigurationError("DATABASE_URL manquant (cf. L026 §4).")
    if not secret_key:
        raise ConfigurationError("SECRET_KEY manquant (cf. L026 §4, L021).")

    api_cfg = raw.get("api", {})
    pagination_cfg = api_cfg.get("pagination", {})
    logging_cfg = raw.get("logging", {})
    securite_cfg = raw.get("securite", {})
    login_cfg = securite_cfg.get("login", {})

    try:
        return Settings(
            app_env=os.environ.get("APP_ENV", "development"),
            app_port=int(os.environ.get("APP_PORT", "8000")),
            log_level=os.environ.get("LOG_LEVEL", logging_cfg.get("level", "INFO")),
            database_url=database_url,
            secret_key=secret_key,
            api_prefix=api_cfg.get("prefix", "/api/v1"),
            pagination_default_size=int(pagination_cfg.get("default_size", 50)),
            pagination_max_size=int(pagination_cfg.get("max_size", 500)),
            session_duree_minutes=int(securite_cfg.get("session_duree_minutes", 60)),
            login_max_tentatives=int(login_cfg.get("max_tentatives", 5)),
            login_fenetre_secondes=int(login_cfg.get("fenetre_secondes", 300)),
        )
    except (TypeError, ValueError) as exc:
        raise ConfigurationError(f"Configuration invalide : {exc}") from exc


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Point d'accès unique aux Settings pour le reste de l'application (mémoïsé)."""
    return load_settings()

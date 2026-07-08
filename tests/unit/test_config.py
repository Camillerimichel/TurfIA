import pytest

from src.core.config import load_settings
from src.core.exceptions import ConfigurationError


@pytest.fixture
def config_file(tmp_path):
    path = tmp_path / "config.yaml"
    path.write_text(
        """
api:
  prefix: /api/v1
  pagination:
    default_size: 20
    max_size: 100
logging:
  level: DEBUG
""",
        encoding="utf-8",
    )
    return path


def test_load_settings_echoue_si_database_url_absent(monkeypatch, config_file):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("SECRET_KEY", "dummy")
    with pytest.raises(ConfigurationError):
        load_settings(config_path=config_file, load_env_file=False)


def test_load_settings_echoue_si_secret_key_absent(monkeypatch, config_file):
    monkeypatch.setenv("DATABASE_URL", "postgresql://localhost/turfia")
    monkeypatch.delenv("SECRET_KEY", raising=False)
    with pytest.raises(ConfigurationError):
        load_settings(config_path=config_file, load_env_file=False)


def test_load_settings_valeurs_correctes(monkeypatch, config_file):
    monkeypatch.setenv("DATABASE_URL", "postgresql://localhost/turfia")
    monkeypatch.setenv("SECRET_KEY", "dummy")
    monkeypatch.delenv("APP_PORT", raising=False)

    settings = load_settings(config_path=config_file, load_env_file=False)

    assert settings.database_url == "postgresql://localhost/turfia"
    assert settings.api_prefix == "/api/v1"
    assert settings.pagination_default_size == 20
    assert settings.pagination_max_size == 100
    assert settings.app_port == 8000
    assert settings.session_duree_minutes == 60
    assert settings.login_max_tentatives == 5
    assert settings.login_fenetre_secondes == 300


def test_load_settings_fichier_introuvable(monkeypatch, tmp_path):
    monkeypatch.setenv("DATABASE_URL", "postgresql://localhost/turfia")
    monkeypatch.setenv("SECRET_KEY", "dummy")
    with pytest.raises(ConfigurationError):
        load_settings(config_path=tmp_path / "absent.yaml", load_env_file=False)

import logging

from src.core.log_db_handler import DbLogHandler


def _record(name: str = "api.errors", level: int = logging.WARNING, message: str = "test") -> logging.LogRecord:
    return logging.LogRecord(name=name, level=level, pathname=__file__, lineno=1, msg=message, args=None, exc_info=None)


def test_emit_ignore_les_logs_du_driver_psycopg():
    """Anti-réentrance : le driver ne doit jamais réentrer dans son propre
    handler (cf. src/core/log_db_handler.py)."""
    handler = DbLogHandler("postgresql://invalide@localhost/inexistant")
    # Ne lève jamais et ne tente aucune connexion (le nom du logger commence par
    # "psycopg") — si une connexion était tentée, le test resterait bloqué
    # jusqu'au connect_timeout au lieu d'être instantané.
    handler.emit(_record(name="psycopg.pool"))


def test_emit_avale_les_erreurs_de_connexion_sans_lever(caplog):
    """Une base indisponible ne doit jamais faire planter l'appelant : seul
    `self.handleError` (stderr, stdlib) est utilisé, jamais `logging.*`."""
    handler = DbLogHandler("postgresql://invalide@localhost:1/inexistant")
    handler.emit(_record())  # ne doit pas lever


def test_niveau_par_defaut_est_warning():
    handler = DbLogHandler("postgresql://invalide@localhost/inexistant")
    assert handler.level == logging.WARNING


def test_niveau_configurable():
    handler = DbLogHandler("postgresql://invalide@localhost/inexistant", niveau="ERROR")
    assert handler.level == logging.ERROR

"""Hiérarchie d'exceptions applicatives — cf. L023 §4.

Note : le type documenté « ImportError » en L023 §4 est nommé ici `ImportationError`
pour ne jamais masquer l'exception native `ImportError` de Python (qui signale un
échec réel d'import de module) — une exception avalée ou mal interceptée à cause
d'un nom identique serait une source de bug silencieux (cf. L019 §6.1).
"""

from __future__ import annotations


class ApplicationError(Exception):
    """Racine de la hiérarchie d'exceptions applicatives TurfIA."""


class ConfigurationError(ApplicationError):
    """Configuration absente, incomplète ou invalide (cf. L026 §2.3, fail-fast)."""


class DatabaseError(ApplicationError):
    """Erreur d'accès ou d'intégrité au niveau de la base de données."""


class ValidationError(ApplicationError):
    """Donnée reçue invalide (type, format, plage de valeurs) — cf. L032.1 §6."""


class BusinessRuleError(ApplicationError):
    """Violation d'une règle métier (cf. L009) — ex. ressource absente ou conflit."""


class ImportationError(ApplicationError):
    """Échec de collecte/importation d'une source de données (cf. L009, L010)."""


class AnalysisError(ApplicationError):
    """Échec d'un calcul du moteur d'analyse (cf. L006, L031.x)."""


class StatisticsError(ApplicationError):
    """Échec d'un calcul statistique (cf. L030.4)."""


class ReportingError(ApplicationError):
    """Échec de génération d'un rapport ou tableau de bord."""


class SecurityError(ApplicationError):
    """Violation d'authentification ou d'autorisation (cf. L021)."""

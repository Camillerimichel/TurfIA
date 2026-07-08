"""Service d'authentification — cf. L015 §7, L021 §3. Aucun code HTTP ici (cf.
L015 §7.2) : les statuts HTTP sont décidés par l'API à partir de `SecurityError`.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from src.core.exceptions import SecurityError
from src.core.security import generer_jeton, hacher_jeton, hacher_mot_de_passe, verifier_mot_de_passe
from src.models.utilisateur import Role, Session, Utilisateur
from src.repositories.audit_repository import AuditRepository
from src.repositories.utilisateur_repository import UtilisateurRepository

# Hash de repli utilisé quand le login est inconnu, pour que la vérification du mot
# de passe s'exécute quand même (bcrypt) — évite qu'un attaquant déduise l'existence
# d'un compte à partir du temps de réponse (cf. L021 §3, aucun avantage à deviner).
_HACHE_FICTIF = hacher_mot_de_passe("mot-de-passe-fictif-temps-constant")


@dataclass(frozen=True)
class SessionAuthentifiee:
    jeton: str  # en clair — retourné une seule fois à l'appelant, jamais stocké tel quel
    expire_le: datetime
    utilisateur: Utilisateur
    role: Role


class AuthService:
    def __init__(
        self,
        utilisateur_repository: UtilisateurRepository,
        audit_repository: AuditRepository,
        duree_session_minutes: int,
    ) -> None:
        self._utilisateurs = utilisateur_repository
        self._audit = audit_repository
        self._duree_session_minutes = duree_session_minutes

    def authentifier(self, login: str, mot_de_passe: str) -> SessionAuthentifiee:
        """Lève `SecurityError` sur identifiants invalides ou compte inactif — le
        message ne distingue jamais "login inconnu" de "mot de passe incorrect"
        (cf. L021 §3, ne pas renseigner un attaquant sur l'existence d'un compte)."""
        utilisateur = self._utilisateurs.get_utilisateur_par_login(login)
        hache_reference = utilisateur.mot_de_passe if utilisateur is not None else _HACHE_FICTIF
        mot_de_passe_valide = verifier_mot_de_passe(mot_de_passe, hache_reference)

        if utilisateur is None or not utilisateur.actif or not mot_de_passe_valide:
            self._audit.enregistrer(utilisateur.id if utilisateur else None, "echec_connexion", objet=login)
            raise SecurityError("Identifiants invalides.")

        role = self._utilisateurs.get_role_par_id(utilisateur.role_id)
        jeton = generer_jeton()
        expire_le = datetime.now(timezone.utc) + timedelta(minutes=self._duree_session_minutes)
        self._utilisateurs.creer_session(
            Session(utilisateur_id=utilisateur.id, jeton_hache=hacher_jeton(jeton), expire_le=expire_le)
        )
        self._utilisateurs.mettre_a_jour_derniere_connexion(utilisateur.id)
        self._audit.enregistrer(utilisateur.id, "connexion")

        return SessionAuthentifiee(jeton=jeton, expire_le=expire_le, utilisateur=utilisateur, role=role)

    def deconnecter(self, jeton: str) -> None:
        jeton_hache = hacher_jeton(jeton)
        resultat = self._utilisateurs.get_utilisateur_par_session_active(jeton_hache)
        self._utilisateurs.revoquer_session(jeton_hache)
        if resultat is not None:
            utilisateur, _ = resultat
            self._audit.enregistrer(utilisateur.id, "deconnexion")

    def utilisateur_courant(self, jeton: str) -> tuple[Utilisateur, Role]:
        """Lève `SecurityError` si le jeton est absent, invalide, expiré, révoqué,
        ou si le compte a été désactivé depuis (cf. L021 §3.3)."""
        resultat = self._utilisateurs.get_utilisateur_par_session_active(hacher_jeton(jeton))
        if resultat is None:
            raise SecurityError("Session invalide ou expirée.")
        self._utilisateurs.marquer_utilisation_session(hacher_jeton(jeton))
        return resultat

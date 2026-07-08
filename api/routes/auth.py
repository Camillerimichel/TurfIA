"""Routes d'authentification — cf. L021 §3, §7.2.1.

`/auth/login` est la seule route en écriture publique (pas d'authentification
préalable) de toute l'API — limitée en débit par (login, adresse IP) pour limiter
les attaques par force brute (cf. L021 §7.2.1).
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Header, Request

from api.dependencies.auth import extraire_jeton
from api.dependencies.services import get_auth_service
from api.schemas.auth import LoginIn, TokenOut, UtilisateurOut
from api.schemas.common import Enveloppe
from src.core.config import get_settings
from src.core.exceptions import SecurityError
from src.core.rate_limiter import LimiteurDebit
from src.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentification"])

# Un seul limiteur partagé pour tout le processus (cf. src/core/rate_limiter.py) — ne
# doit pas être recréé à chaque requête, sinon la fenêtre glissante ne sert à rien.
_settings = get_settings()
_limiteur_login = LimiteurDebit(_settings.login_max_tentatives, _settings.login_fenetre_secondes)


@router.post("/login", response_model=Enveloppe[TokenOut])
def login(payload: LoginIn, request: Request, service: AuthService = Depends(get_auth_service)) -> Enveloppe[TokenOut]:
    adresse_ip = request.client.host if request.client else "inconnue"
    if not _limiteur_login.autoriser(f"{payload.login}:{adresse_ip}"):
        raise HTTPException(status_code=429, detail="Trop de tentatives de connexion, réessayez plus tard.")

    try:
        session = service.authentifier(payload.login, payload.mot_de_passe)
    except SecurityError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc

    return Enveloppe(
        data=TokenOut(
            jeton=session.jeton,
            expire_le=session.expire_le,
            utilisateur=UtilisateurOut(
                id=session.utilisateur.id,
                login=session.utilisateur.login,
                nom=session.utilisateur.nom,
                role=session.role.nom,
            ),
        )
    )


@router.post("/logout", response_model=Enveloppe[dict])
def logout(
    authorization: str | None = Header(default=None), service: AuthService = Depends(get_auth_service)
) -> Enveloppe[dict]:
    jeton = extraire_jeton(authorization)
    service.deconnecter(jeton)
    return Enveloppe(data={"deconnecte": True})

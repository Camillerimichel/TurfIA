"""Crée un compte utilisateur (bootstrap du premier compte Administrateur, ou tout
autre compte par la suite) — cf. L021 §3.1. Usage :

    python scripts/creer_utilisateur.py --login jdupont --role Administrateur

Le mot de passe est saisi de façon interactive (jamais en argument de ligne de
commande, pour ne pas se retrouver dans l'historique du shell) et haché avant
stockage (cf. L021 §3.2). Une fois l'authentification en place, il n'existe pas
d'autre moyen de créer un compte (l'API ne l'expose pas : la création d'utilisateurs
n'est pas dans le périmètre RBAC actuel, cf. PROJECT_STATE.md).
"""

from __future__ import annotations

import argparse
import getpass
import sys

from src.core.security import hacher_mot_de_passe
from src.database.connection import session
from src.models.utilisateur import Utilisateur
from src.repositories.utilisateur_repository import UtilisateurRepository

ROLES_VALIDES = ("Administrateur", "Analyste", "Consultation", "Automatisation")


def run() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--login", required=True)
    parser.add_argument("--role", required=True, choices=ROLES_VALIDES)
    parser.add_argument("--nom", default=None)
    parser.add_argument("--email", default=None)
    args = parser.parse_args()

    mot_de_passe = getpass.getpass("Mot de passe : ")
    confirmation = getpass.getpass("Confirmer le mot de passe : ")
    if mot_de_passe != confirmation:
        print("Les deux saisies ne correspondent pas.", file=sys.stderr)
        return 1
    if len(mot_de_passe) < 8:
        print("Le mot de passe doit compter au moins 8 caractères (cf. L021 §3.2).", file=sys.stderr)
        return 1

    with session() as conn:
        repo = UtilisateurRepository(conn)

        if repo.get_utilisateur_par_login(args.login) is not None:
            print(f"Le login '{args.login}' existe déjà.", file=sys.stderr)
            return 1

        role = repo.get_role_par_nom(args.role)
        if role is None:
            print(f"Rôle '{args.role}' introuvable en base (cf. sql/schema/05_techniques.sql).", file=sys.stderr)
            return 1

        utilisateur = repo.creer_utilisateur(
            Utilisateur(
                login=args.login,
                mot_de_passe=hacher_mot_de_passe(mot_de_passe),
                role_id=role.id,
                nom=args.nom,
                email=args.email,
            )
        )

    print(f"Utilisateur créé : #{utilisateur.id} {utilisateur.login} ({args.role})")
    return 0


if __name__ == "__main__":
    sys.exit(run())

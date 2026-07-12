"""Schémas du module Administration — cf. L018 §10."""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class JournalOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    date_evenement: datetime
    niveau: str
    composant: str | None = None
    correlation_id: str | None = None
    message: str
    exception: str | None = None


class TacheOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nom: str
    categorie: str | None = None
    debut: datetime
    fin: datetime | None = None
    duree_ms: int | None = None
    statut: str
    commentaire: str | None = None


class ParametreOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cle: str
    valeur: str
    type: str
    description: str | None = None
    date_modification: datetime


class ParametrePatchIn(BaseModel):
    valeur: str


class VersionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    version: str
    commit_git: str | None = None
    branche: str | None = None
    date_publication: datetime
    commentaire: str | None = None


class EtatSupervisionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    base_de_donnees_ok: bool
    latence_db_ms: float | None = None
    espace_disque_disponible_octets: int
    taches_en_echec_24h: int
    demarrage_processus: datetime
    uptime_secondes: float


class RejeuIn(BaseModel):
    """Payload du moteur de rejeu (cf. L031.7 §4, `RejeuService.rejouer`) —
    déclenché depuis l'interface HTML (Statistiques) au lieu du seul CLI
    `scripts/rejouer_versions.py` (retour utilisateur, 2026-07-12)."""

    version_modele: str
    date_debut: date
    date_fin: date
    poids_score: dict[str, float] | None = None
    poids_risque: dict[str, float] | None = None
    commentaire: str | None = None


class ErreurCourseOut(BaseModel):
    course_id: int
    message: str


class RapportAnalyseJourOut(BaseModel):
    nb_courses: int
    nb_erreurs: int
    nb_deja_parties: int = 0
    erreurs: list[ErreurCourseOut]


class TacheCronOut(BaseModel):
    """Une ligne du tableau de bord Cron — dernière exécution connue d'une
    tâche quotidienne (`nom` fixe, cf. `api/routes/administration.py`), ou
    `derniere_tache=None` si elle n'a jamais tourné."""

    nom: str
    libelle: str
    derniere_tache: TacheOut | None = None


class JournalCronOut(BaseModel):
    """Dernières lignes des fichiers de log launchd (`logs/rafraichir_et_
    analyser*.log`) — pas d'archive, juste la fin du fichier courant."""

    sortie: str
    erreurs: str

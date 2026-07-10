"""Teste les fonctions pures de api/routes/analyses.py — traduction des
combinaisons de paris en libellés lisibles (cf. L018 §6-7), en particulier
l'expansion Quinté Flexi en combinaisons individuelles de 5 chevaux (cf.
L031.6 §5 : un ticket Flexi joue TOUTES les combinaisons de 5 parmi la
sélection retenue, pas une seule).
"""

from api.routes.analyses import _pari_vers_out, _resoudre_combinaison, _sous_combinaisons_quinte
from src.models.analyse import Pari
from src.models.course import PartantDetail


def _detail(partant_id: int, numero: int, nom: str) -> PartantDetail:
    return PartantDetail(id=partant_id, course_id=1, cheval_id=partant_id, numero=numero, cheval_nom=nom)


PARTANTS_DETAIL = {
    p.id: p
    for p in [
        _detail(1, 1, "Alpha"),
        _detail(2, 2, "Beta"),
        _detail(3, 3, "Gamma"),
        _detail(4, 4, "Delta"),
        _detail(5, 5, "Epsilon"),
        _detail(6, 6, "Zeta"),
    ]
}


def test_resoudre_combinaison_simple():
    assert _resoudre_combinaison("1-2", PARTANTS_DETAIL) == "N°1 Alpha + N°2 Beta"


def test_resoudre_combinaison_partant_introuvable_retombe_sur_lidentifiant():
    assert _resoudre_combinaison("1-999", PARTANTS_DETAIL) == "N°1 Alpha + partant #999"


def test_sous_combinaisons_quinte_none_si_cinq_chevaux_ou_moins():
    """Une seule combinaison possible avec 5 chevaux : `combinaison_lisible`
    suffit déjà, pas besoin d'expansion."""
    assert _sous_combinaisons_quinte("1-2-3-4-5", mise=2.0, partants_detail=PARTANTS_DETAIL) is None


def test_sous_combinaisons_quinte_expanse_les_combinaisons_de_cinq():
    """6 chevaux sélectionnés -> C(6,5) = 6 combinaisons de 5, chacune une
    ligne à part, mise totale répartie également entre elles."""
    libelles, mise_par_combinaison = _sous_combinaisons_quinte(
        "1-2-3-4-5-6", mise=12.0, partants_detail=PARTANTS_DETAIL
    )
    assert len(libelles) == 6  # C(6,5)
    assert mise_par_combinaison == 2.0
    # Chaque combinaison omet exactement un des 6 chevaux ; celle sans Zeta (N°6) :
    assert "N°1 Alpha + N°2 Beta + N°3 Gamma + N°4 Delta + N°5 Epsilon" in libelles
    # Aucune combinaison ne doit lister les 6 chevaux à la fois.
    assert all(libelle.count(" + ") == 4 for libelle in libelles)


def test_pari_vers_out_quinte_flexi_porte_les_sous_combinaisons():
    pari = Pari(analyse_id=1, type_pari="Quinté Flexi", id=1, combinaison="1-2-3-4-5-6", mise=12.0)
    out = _pari_vers_out(pari, PARTANTS_DETAIL)
    assert out.sous_combinaisons is not None
    assert len(out.sous_combinaisons) == 6
    assert out.mise_par_combinaison == 2.0


def test_pari_vers_out_autre_type_pari_sans_sous_combinaisons():
    pari = Pari(analyse_id=1, type_pari="Couplé Gagnant", id=1, combinaison="1-2", mise=10.0)
    out = _pari_vers_out(pari, PARTANTS_DETAIL)
    assert out.sous_combinaisons is None
    assert out.mise_par_combinaison is None
    assert out.combinaison_lisible == "N°1 Alpha + N°2 Beta"

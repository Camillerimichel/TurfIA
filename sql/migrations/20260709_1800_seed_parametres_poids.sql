-- Sème les pondérations par défaut dans `parametre` (cf. L011 §10.4, L026 §3.3,
-- module Administration L018 §10 « gérer les paramètres »). Valeurs identiques à
-- PONDERATIONS_PAR_DEFAUT (src/algorithms/score.py, src/algorithms/risque.py) :
-- comportement strictement inchangé au déploiement, seule une modification
-- ultérieure via PATCH /administration/parametres/{cle} change le résultat.

INSERT INTO parametre (cle, valeur, type, description) VALUES
    ('poids_score.marche', '1.0', 'Decimal', 'Pondération sous-score Marché (cf. L031.2 §6)'),
    ('poids_score.presse', '1.0', 'Decimal', 'Pondération sous-score Presse'),
    ('poids_score.forme', '1.0', 'Decimal', 'Pondération sous-score Forme'),
    ('poids_score.aptitude', '1.0', 'Decimal', 'Pondération sous-score Aptitude'),
    ('poids_score.professionnels', '1.0', 'Decimal', 'Pondération sous-score Professionnels'),
    ('poids_score.historique', '1.0', 'Decimal', 'Pondération sous-score Historique'),
    ('poids_score.value', '1.0', 'Decimal', 'Pondération sous-score Value'),
    ('poids_score.contexte', '1.0', 'Decimal', 'Pondération sous-score Contexte'),
    ('poids_risque.marche', '1.0', 'Decimal', 'Pondération sous-risque Marché (cf. L031.3 §5)'),
    ('poids_risque.presse', '1.0', 'Decimal', 'Pondération sous-risque Presse'),
    ('poids_risque.course', '1.0', 'Decimal', 'Pondération sous-risque Course'),
    ('poids_risque.terrain', '1.0', 'Decimal', 'Pondération sous-risque Terrain'),
    ('poids_risque.historique', '1.0', 'Decimal', 'Pondération sous-risque Historique'),
    ('poids_risque.contexte', '1.0', 'Decimal', 'Pondération sous-risque Contexte'),
    ('poids_risque.statistiques', '1.0', 'Decimal', 'Pondération sous-risque Statistiques')
ON CONFLICT (cle) DO NOTHING;

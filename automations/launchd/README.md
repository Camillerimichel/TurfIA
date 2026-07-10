# Tâche planifiée locale (launchd)

Automatisation "collecte + analyse + statistiques du jour" (cf.
`scripts/rafraichir_et_analyser_jour.py`), déclenchée toutes les heures de 9h
à 23h (fenêtre volontairement large pour couvrir les réunions en nocturne) :

1. Collecte du programme du jour (cotes, résultats si déjà connus).
2. Analyse de chaque course pas encore partie — le script arrête de lui-même
   de relancer l'analyse 30 minutes avant le départ de la dernière course
   réelle du jour (`CourseRepository.get_derniere_heure_depart`), pas la
   planification `launchd`. Chaque passage vise une nouvelle version
   d'analyse (jamais un conflit avec la précédente) : la décision jouer/ne
   pas jouer peut donc changer d'une heure à l'autre, dans les deux sens.
3. Contrôle ROI réel (rapports définitifs PMU) + recalcul des 6 tables
   statistiques — sans fenêtre de coupure (utile justement pour les courses
   déjà parties ; `ControleRoiService` ignore de lui-même celles trop
   récentes pour avoir des rapports homologués).

Décision du 2026-07-09 : pas de scheduler générique dans l'application (cf.
PROJECT_STATE.md) — `launchd` (natif macOS) appelle le script existant, qui
réutilise les mêmes services que l'API/l'Administration HTML (cf. L033
ADR-002).

## Installer

```bash
cp "automations/launchd/com.turfia.rafraichir-analyser.plist" ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.turfia.rafraichir-analyser.plist
```

## Vérifier

```bash
launchctl list | grep turfia
tail -f logs/rafraichir_et_analyser.log
```

Les exécutions sont aussi visibles dans la page Administration de
l'interface HTML (section Automatisations), au même titre qu'un
déclenchement manuel.

## Désinstaller

```bash
launchctl unload ~/Library/LaunchAgents/com.turfia.rafraichir-analyser.plist
rm ~/Library/LaunchAgents/com.turfia.rafraichir-analyser.plist
```

## Forcer une exécution immédiate (sans attendre l'heure programmée)

```bash
launchctl start com.turfia.rafraichir-analyser
```

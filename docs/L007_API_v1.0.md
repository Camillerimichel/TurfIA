# TurfIA

## L007_API_v1.0

**Version :** 1.0  
**Statut :** Validé  
**Objet :** Spécification de l'API interne TurfIA

---

## Objectif

Ce livrable décrit l'API interne de TurfIA. L'API doit permettre d'exposer les données de référence, les courses, les partants, les analyses, les résultats, les historiques, les statistiques et les tâches planifiées.

L'API est conçue comme une interface interne entre la base SQL, le moteur d'analyse, les scripts d'automatisation et les interfaces de consultation.

---

## Principes

L'API TurfIA respecte les principes suivants :

- endpoints stables et versionnés ;
- séparation entre lecture et écriture ;
- traçabilité des traitements ;
- absence de données codées en dur ;
- retour explicite des erreurs ;
- conservation de l'historique ;
- compatibilité avec des exports JSON et CSV ;
- possibilité d'extension vers une interface web ou mobile.

---

## Convention de versionnement

La première version de l'API est exposée sous le préfixe :

```text
/api/v1
```

Toute évolution incompatible doit être introduite dans une nouvelle version majeure.

---

## Formats

### Format d'entrée

Les écritures utilisent principalement le format JSON.

### Format de sortie

Les réponses sont retournées en JSON par défaut.

Les exports peuvent être produits en :

- JSON ;
- CSV ;
- PDF pour les rapports d'analyse si un générateur dédié est branché ultérieurement.

---

## Statuts de réponse

| Code | Usage |
|-----:|-------|
| 200 | Lecture ou traitement réussi |
| 201 | Ressource créée |
| 400 | Requête invalide |
| 404 | Ressource introuvable |
| 409 | Conflit de données ou analyse déjà finalisée |
| 422 | Données insuffisantes ou incohérentes |
| 500 | Erreur interne |

---

## Endpoints de santé

### GET /api/v1/health

Vérifie que l'API est active.

Réponse attendue :

```json
{
  "status": "ok",
  "service": "TurfIA",
  "version": "1.0"
}
```

### GET /api/v1/status

Retourne l'état général du système.

Champs indicatifs :

- statut API ;
- statut base SQL ;
- dernière pré-analyse ;
- dernière analyse finale ;
- dernier contrôle de résultat ;
- version du modèle.

---

## Courses

### GET /api/v1/courses

Liste les courses enregistrées.

Filtres possibles :

- date ;
- hippodrome ;
- discipline ;
- statut ;
- quinté uniquement.

### GET /api/v1/courses/{course_id}

Retourne le détail d'une course.

### POST /api/v1/courses

Crée une course à partir des données collectées.

Données minimales :

- date ;
- hippodrome ;
- nom ;
- numéro ;
- heure officielle ;
- discipline ;
- distance ;
- nombre de partants.

### PATCH /api/v1/courses/{course_id}

Met à jour les informations non définitives d'une course.

Une course liée à une analyse finale ne doit pas être modifiée sans créer une nouvelle version de données.

---

## Partants

### GET /api/v1/courses/{course_id}/partants

Liste les partants d'une course.

### GET /api/v1/partants/{partant_id}

Retourne le détail d'un partant.

### POST /api/v1/courses/{course_id}/partants

Ajoute un partant à une course.

### PATCH /api/v1/partants/{partant_id}

Met à jour les données d'un partant avant analyse finale.

Champs typiques :

- nom ;
- numéro ;
- entraîneur ;
- jockey ou driver ;
- musique ;
- valeur handicap ;
- statut partant ou non-partant.

---

## Cotes

### GET /api/v1/courses/{course_id}/cotes

Retourne les cotes enregistrées pour une course.

### POST /api/v1/cotes

Ajoute une observation de cote.

Champs attendus :

- course_id ;
- partant_id ;
- source ;
- cote ;
- horodatage.

Les cotes sont historisées. Une cote existante ne doit pas être écrasée.

---

## Analyses

### GET /api/v1/analyses

Liste les analyses enregistrées.

Filtres possibles :

- date ;
- course_id ;
- type d'analyse ;
- score minimum ;
- décision de jeu.

### GET /api/v1/analyses/{analyse_id}

Retourne une analyse complète.

### POST /api/v1/analyses/preanalyse

Déclenche une pré-analyse sur une course.

Données attendues :

- course_id ;
- version du modèle ;
- sources de données utilisées.

### POST /api/v1/analyses/finale

Déclenche l'analyse finale d'une course.

Données attendues :

- course_id ;
- analyse_precedente_id ;
- version du modèle ;
- confirmation des non-partants ;
- dernières cotes disponibles.

### Règle d'immutabilité

Une analyse validée ne doit pas être modifiée. Une correction doit créer une nouvelle version liée à l'analyse d'origine.

---

## Résultats

### GET /api/v1/courses/{course_id}/resultat

Retourne le résultat officiel d'une course.

### POST /api/v1/resultats

Enregistre le résultat officiel.

Champs attendus :

- course_id ;
- arrivée officielle ;
- rapports PMU ;
- non-partants confirmés ;
- source ;
- horodatage.

---

## Contrôles de résultats

### POST /api/v1/controles/resultats

Déclenche le contrôle d'une analyse finale.

Données attendues :

- analyse_id ;
- resultat_id ;
- budget de référence ;
- version du moteur de contrôle.

Sorties :

- gains ;
- profit ou perte ;
- ROI course ;
- ROI cumulé ;
- analyse critique.

---

## Historique

### GET /api/v1/historique

Retourne l'historique des analyses et performances.

Filtres possibles :

- période ;
- hippodrome ;
- discipline ;
- niveau de score ;
- décision ;
- type de pari.

### GET /api/v1/historique/{historique_id}

Retourne une ligne d'historique détaillée.

---

## Statistiques

### GET /api/v1/statistiques/globales

Retourne les statistiques globales TurfIA.

Indicateurs :

- nombre de courses analysées ;
- nombre de courses jouées ;
- nombre de courses évitées ;
- taux de réussite ;
- mise cumulée ;
- gains cumulés ;
- profit cumulé ;
- ROI global.

### GET /api/v1/statistiques/confiance

Retourne les statistiques par tranche de confiance.

### GET /api/v1/statistiques/paris

Retourne les statistiques par type de pari.

### GET /api/v1/statistiques/hippodromes

Retourne les statistiques par hippodrome.

---

## Paris

### GET /api/v1/analyses/{analyse_id}/paris

Retourne les paris proposés pour une analyse.

### POST /api/v1/paris

Crée une proposition de pari liée à une analyse.

Champs attendus :

- analyse_id ;
- type de pari ;
- sélection ;
- mise ;
- justification.

Les paris proposés par une analyse finale doivent être conservés même si le résultat est défavorable.

---

## Tâches planifiées

### GET /api/v1/taches

Liste les tâches planifiées.

### POST /api/v1/taches/preanalyse

Déclenche ou programme une pré-analyse quotidienne.

### POST /api/v1/taches/analyse-finale

Déclenche ou programme une analyse finale avant départ.

### POST /api/v1/taches/controle-resultat

Déclenche ou programme le contrôle de résultat du lendemain.

### GET /api/v1/taches/{tache_id}/logs

Retourne les journaux d'exécution d'une tâche.

---

## Exports

### GET /api/v1/exports/analyses

Exporte les analyses sur une période.

### GET /api/v1/exports/historique

Exporte l'historique complet.

### GET /api/v1/exports/statistiques

Exporte les statistiques globales et détaillées.

Formats possibles :

- JSON ;
- CSV ;
- PDF si le module de génération de rapports est disponible.

---

## Gestion des erreurs

Les erreurs doivent retourner un objet structuré :

```json
{
  "error": true,
  "code": "DONNEES_INSUFFISANTES",
  "message": "Les cotes de la course sont indisponibles.",
  "blocking": true
}
```

Les erreurs bloquantes empêchent la validation de l'analyse. Les erreurs non bloquantes doivent être conservées dans la trace de l'analyse.

---

## Sécurité minimale

L'API étant interne dans la première version, la sécurité minimale attendue est :

- séparation des environnements ;
- journalisation des écritures ;
- contrôle des actions destructives ;
- absence d'informations sensibles dans les logs ;
- préparation à une authentification par jeton si l'API est exposée ultérieurement.

---

## Journalisation

Chaque appel d'écriture doit enregistrer :

- endpoint appelé ;
- horodatage ;
- utilisateur ou processus appelant ;
- ressource affectée ;
- statut ;
- message d'erreur éventuel.

Cette journalisation est nécessaire pour garantir la traçabilité du projet.

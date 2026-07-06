# L026 — Gestion de la configuration

## 0. Métadonnées du document

| Champ | Valeur |
| --- | --- |
| Identifiant | L026 |
| Niveau documentaire | Spécification technique (cf. L001 §3) |
| Version | 1.0 |
| Documents liés | L010 (déploiement), L021 (sécurité), L027 (gestion des versions Git) |

## 1. Objectif

### 1.1 Finalité

La gestion de la configuration regroupe l'ensemble des paramètres nécessaires au fonctionnement de TurfIA.

Elle poursuit plusieurs objectifs :

- séparer la configuration du code ;
- faciliter le déploiement ;
- sécuriser les informations sensibles ;
- simplifier les évolutions ;
- garantir la reproductibilité des environnements.

Aucun paramètre spécifique à un environnement ne doit être codé en dur.

---

## 2. Principes

### 2.1 Séparation

Les éléments suivants sont totalement indépendants :

- code source ;
- configuration ;
- données ;
- secrets.

Cette séparation permet de déployer une même version logicielle sur plusieurs environnements.

---

### 2.2 Centralisation

L'ensemble des paramètres est regroupé dans un mécanisme unique de configuration.

Les modules applicatifs ne lisent jamais directement les variables d'environnement.

### 2.3 Validation au démarrage (fail-fast)

Conformément à l'ADR-001 de L010, une configuration incomplète ou
invalide empêche le démarrage de l'application plutôt que de produire
un comportement dégradé silencieux. Cette règle est reprise en détail
au §6.

---

## 3. Types de configuration

### 3.1 Configuration système

Elle comprend notamment :

- ports réseau ;
- chemins de fichiers ;
- paramètres Docker ;
- configuration Nginx ;
- planification des tâches.

---

### 3.2 Configuration applicative

Elle comprend notamment :

- paramètres TurfIA ;
- seuils de confiance ;
- budgets de référence ;
- pondérations ;
- paramètres statistiques.

Ces éléments peuvent évoluer sans modification du code.

---

### 3.3 Configuration métier

Les paramètres métier sont stockés en base de données.

Exemples :

- score minimum de jeu ;
- budget par niveau de confiance ;
- pondération des critères ;
- paramètres des algorithmes.

### 3.4 Distinction avec le registre des règles métier

Un paramètre de configuration métier (ex. un seuil) diffère d'une règle
métier (ex. la logique d'application de ce seuil, cf. L009 §5.2) : le
paramètre est une valeur modifiable sans revue de code, la règle est un
comportement qui suit le cycle de vie et la revue définis en L009.
Toute modification d'un paramètre de configuration métier reste
néanmoins historisée (cf. §8) afin de préserver la comparabilité des
analyses (cf. ADR-002 de L001).

---

## 4. Variables d'environnement

### 4.1 Objectif

Les informations sensibles sont fournies via des variables d'environnement.

Exemples :

- connexion SQL ;
- identifiants ;
- clés API ;
- certificats ;
- paramètres de sécurité.

---

### 4.2 Exemple

```text
APP_ENV=production

APP_PORT=8000

DATABASE_URL=...

SECRET_KEY=...

LOG_LEVEL=INFO
```

Le fichier `.env.example` documente les variables attendues.

---

## 5. Environnements

### 5.1 Développement

Caractéristiques :

- journalisation détaillée ;
- données de test ;
- outils de diagnostic activés.

---

### 5.2 Préproduction

Objectifs :

- validation complète ;
- performances proches de la production ;
- données représentatives.

---

### 5.3 Production

Caractéristiques :

- sécurité renforcée ;
- journalisation maîtrisée ;
- supervision permanente ;
- sauvegardes actives.

---

## 6. Chargement

Au démarrage de l'application :

1. lecture des variables d'environnement ;
2. chargement des fichiers de configuration ;
3. lecture des paramètres en base ;
4. validation ;
5. mise à disposition des composants.

En cas d'erreur, le démarrage est interrompu.

---

## 7. Validation

Chaque paramètre est contrôlé avant son utilisation.

Les contrôles portent notamment sur :

- présence ;
- type ;
- format ;
- plage de valeurs ;
- cohérence.

Une configuration invalide empêche le lancement de l'application.

---

## 8. Versionnement

Les fichiers de configuration non sensibles sont versionnés dans Git.

Les secrets ne sont jamais versionnés.

Chaque évolution importante est documentée.

---

## 9. Sécurité

Les secrets respectent les règles suivantes :

- stockage hors du dépôt Git ;
- accès limité ;
- rotation régulière ;
- journalisation des modifications.

Les mots de passe ne sont jamais stockés en clair.

---

## 10. Évolutivité

Le système de configuration permet d'ajouter facilement :

- de nouveaux paramètres ;
- de nouveaux environnements ;
- de nouveaux services ;
- de nouveaux modules.

Cette architecture garantit une configuration homogène et facilement maintenable sur l'ensemble de TurfIA.

---

## Historique

| Version | Description |
| --- | --- |
| 1.0 | Version initiale |
| 1.1 | Enrichissement industriel : métadonnées du document, validation fail-fast au démarrage, distinction entre paramètre de configuration métier et règle métier (renvoi vers L009). Correction de structure : le contenu relatif à la gestion des versions Git, précédemment dupliqué en fin de ce fichier sous un en-tête « L027 », a été fusionné dans le document dédié [L027_GESTION_VERSIONS_GIT_v1.0.md](L027_GESTION_VERSIONS_GIT_v1.0.md) auquel il appartient, sans perte d'information |

*Fin du document L026.*
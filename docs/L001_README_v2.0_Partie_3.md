# L001_README_v2.0.md --- Partie 3/3

## 9. Gouvernance documentaire

Le dépôt Git constitue la référence unique du projet. Toute évolution de
l'architecture est documentée avant son implémentation. Les décisions
majeures sont consignées sous forme d'Architecture Decision Records
(ADR) afin d'assurer leur traçabilité.

Les documents du Software Architecture Document décrivent les
responsabilités, les contraintes, les interactions et les principes de
conception. Les documents techniques détaillent uniquement les
mécanismes d'implémentation.

### 9.1 Cycle de vie d'un document

  Étape          Description                                             Responsable
  -------------- -------------------------------------------------------- --------------------
  Rédaction       Création ou modification du contenu                     Auteur désigné
  Revue           Vérification de la cohérence avec les autres documents  Architecte logiciel
  Approbation     Validation formelle et incrémentation de version        Propriétaire du SAD
  Publication     Commit dans le dépôt avec message explicite (cf. L027)  Auteur désigné
  Réévaluation    Contrôle périodique de péremption du contenu            Gouvernance projet (L028)

### 9.2 Règles de gestion des versions documentaires

-   toute modification substantielle incrémente le numéro de version
    majeure (1.0 → 2.0) et conserve les versions antérieures dans le
    dépôt (aucune suppression) ;
-   une modification mineure (correction, clarification) incrémente une
    version mineure documentée dans l'historique de chaque fichier ;
-   la numérotation des livrables (L001…L039, sous-numérotation
    `Lxxx.y`) est stable et ne doit jamais être réutilisée pour un
    contenu différent.

## 10. Relations avec les autres documents

Le présent document introduit l'ensemble du corpus documentaire :

-   L002 : Vision
-   L003 : Architecture générale
-   L004 : Modèle de données
-   L005 : Workflow
-   L006 : Algorithmes
-   L007 : API
-   L008 : Base SQL
-   L009 : Règles métier
-   L010 : Déploiement
-   L032.2 à L039 : architecture transverse.

Chaque chapitre complète le précédent sans redondance.

### 10.1 Matrice de traçabilité (extrait)

  Préoccupation (concern)          Documents adressant la préoccupation
  --------------------------------- ---------------------------------------
  Fiabilité des données              L009, L010, L023
  Performance                        L024, L036
  Sécurité                           L021, L034
  Journalisation et traçabilité      L022, L037
  Reprise après incident             L025, L033, L038
  Évolution de l'architecture        L039, L028

## 11. Convention documentaire

Chaque document du SAD adopte la même structure :

1.  Objet
2.  Périmètre
3.  Principes
4.  Architecture
5.  Responsabilités
6.  Contraintes
7.  ADR
8.  Interactions
9.  Références

Cette homogénéité facilite la maintenance et la compréhension globale du
projet. Les documents techniques (L011 à L032.1) adoptent une structure
allégée mais conservent systématiquement les sections Objectif,
Architecture/Modèle, Règles, Sécurité et Interactions lorsque
pertinentes.

### 11.1 Conventions de notation

-   les exemples JSON illustrent le format réel mais ne sont pas
    exhaustifs ;
-   les blocs `text` représentent des schémas simplifiés, non des
    diagrammes normatifs ;
-   les diagrammes Mermaid constituent des vues au sens ISO/IEC/IEEE
    42010 et doivent rester synchronisés avec le code lorsqu'ils
    décrivent un flux d'exécution.

## 12. Conclusion

Le Software Architecture Document constitue la référence architecturale
de TurfIA. Il garantit la cohérence des décisions de conception,
facilite les évolutions futures et assure la séparation entre
architecture et implémentation.

Les principes décrits dans ce document s'imposent à tous les composants
de la plateforme.

## 13. Hypothèses et limites du présent document

Ce document suppose que le lecteur dispose de connaissances générales
en architecture logicielle. Le glossaire des termes spécifiques au
domaine hippique et à TurfIA est fourni en L029. Ce document ne fixe
pas de calendrier de mise en œuvre : celui-ci relève de la gouvernance
projet (L028).

## Historique

  Version   Description
  --------- -------------------------------------------------------------
  1.0       Première version
  2.0       Réécriture complète orientée Software Architecture Document
  2.1       Enrichissement niveau industriel : parties prenantes, ADR détaillées, matrice de traçabilité, cycle de vie documentaire, risques et hypothèses (alignement ISO/IEC/IEEE 42010)

*Fin du document L001.*

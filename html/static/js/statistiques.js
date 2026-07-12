// Page Statistiques (cf. L018 §9) — les 6 tables déjà exposées par l'API.

initialiserEntete();

function formaterValeur(valeur) {
  if (valeur === null || valeur === undefined) return "n/a";
  if (typeof valeur === "number") return Number.isInteger(valeur) ? valeur : valeur.toFixed(2);
  if (typeof valeur === "string" && MOTIF_DATE_ISO.test(valeur)) return formaterDateHeure(valeur);
  return valeur;
}

function construireTableau(lignes, colonnes) {
  const table = document.createElement("table");
  const entete = document.createElement("thead");
  const ligneEntete = document.createElement("tr");
  for (const colonne of colonnes) {
    const cellule = document.createElement("th");
    cellule.textContent = colonne.libelle;
    ligneEntete.appendChild(cellule);
  }
  entete.appendChild(ligneEntete);
  table.appendChild(entete);

  const corps = document.createElement("tbody");
  if (lignes.length === 0) {
    const ligneVide = document.createElement("tr");
    const cellule = document.createElement("td");
    cellule.colSpan = colonnes.length;
    cellule.textContent = "Aucune donnée.";
    ligneVide.appendChild(cellule);
    corps.appendChild(ligneVide);
  }
  for (const ligne of lignes) {
    const tr = document.createElement("tr");
    for (const colonne of colonnes) {
      const cellule = document.createElement("td");
      const brut = ligne[colonne.cle];
      if (colonne.carte) {
        // Résout un identifiant (hippodrome_id/discipline_id) vers son nom —
        // retour utilisateur : « remplace les chiffres par les noms ».
        // Repli sur l'identifiant brut si la carte n'a pas cette entrée
        // (référentiel pas encore chargé/supprimé), jamais une case vide.
        cellule.textContent = colonne.carte.get(brut) ?? `${colonne.prefixe} #${brut}`;
      } else if (colonne.montant) {
        cellule.textContent = formaterMontant(brut);
      } else {
        cellule.textContent = formaterValeur(brut);
      }
      tr.appendChild(cellule);
    }
    corps.appendChild(tr);
  }
  table.appendChild(corps);
  return table;
}

async function chargerSectionSimple(chemin, idSection, colonnes) {
  const conteneur = document.getElementById(idSection);
  try {
    const lignes = await apiFetch(chemin);
    conteneur.innerHTML = "";
    conteneur.appendChild(construireTableau(lignes, colonnes));
  } catch (erreur) {
    conteneur.textContent = `Erreur : ${erreur.message}`;
  }
}

function construireSousTableauJSON(brutJSON, colonnes) {
  if (!brutJSON) {
    const p = document.createElement("p");
    p.textContent = "Non disponible pour cette ligne.";
    return p;
  }
  const lignes = JSON.parse(brutJSON);
  return construireTableau(lignes, colonnes);
}

async function chargerModeles() {
  const conteneur = document.getElementById("section-modeles");
  try {
    const [tousLesModeles, nomHippodrome] = await Promise.all([
      apiFetch("/statistiques/modeles"),
      chargerCarteReferentiel("/hippodromes", "nom"),
    ]);
    conteneur.innerHTML = "";
    // Ne montre que les vrais rejeux ici — retour utilisateur (2026-07-12) :
    // l'agrégation automatique par statut Pré/Finale (source="automatique",
    // cf. StatistiqueRepository.calculer_modeles) n'est pas une comparaison
    // de modèles exploitable (pas de jeu de poids différent), elle continue
    // d'exister en base mais n'a plus sa place dans ce bloc.
    const modeles = tousLesModeles.filter((m) => m.source === "rejeu");
    if (modeles.length === 0) {
      conteneur.textContent = "Aucun rejeu manuel exécuté pour l'instant — utilise le formulaire ci-dessus.";
      return;
    }
    for (const modele of modeles) {
      const bloc = document.createElement("div");
      bloc.className = "bloc-modele";

      const titre = document.createElement("h3");
      titre.textContent = `Version « ${modele.version_modele} »`;
      bloc.appendChild(titre);

      const periode = document.createElement("p");
      periode.className = "note";
      periode.textContent =
        `Rejeu du ${formaterValeur(modele.date_debut)} au ${formaterValeur(modele.date_fin)} — ` +
        `calculé le ${modele.cree_le ? formaterDateHeure(modele.cree_le) : "n/a"}`;
      bloc.appendChild(periode);

      const resume = document.createElement("p");
      resume.textContent =
        `${formaterValeur(modele.nb_courses)} course(s) — ROI ${formaterValeur(modele.roi)} % — ` +
        `taux de réussite ${formaterValeur(modele.taux_reussite)} % — ` +
        `drawdown ${formaterMontant(modele.drawdown)} € — stabilité ${formaterValeur(modele.stabilite)}`;
      bloc.appendChild(resume);

      if (modele.commentaire) {
        const commentaire = document.createElement("p");
        commentaire.className = "note";
        commentaire.textContent = modele.commentaire;
        bloc.appendChild(commentaire);
      }

      const details = document.createElement("details");
      const summary = document.createElement("summary");
      summary.textContent = "Détail par tranche de score / hippodrome / type de pari";
      details.appendChild(summary);

      const titreScore = document.createElement("h4");
      titreScore.textContent = "Par tranche de score";
      details.appendChild(titreScore);
      details.appendChild(
        construireSousTableauJSON(modele.roi_par_score, [
          { libelle: "Score min", cle: "score_min" },
          { libelle: "Score max", cle: "score_max" },
          { libelle: "Courses", cle: "nb_courses" },
          { libelle: "Gagnantes", cle: "nb_gagnantes" },
          { libelle: "ROI %", cle: "roi" },
          { libelle: "Taux réussite (courses) %", cle: "taux_reussite" },
        ])
      );

      const titreHippodrome = document.createElement("h4");
      titreHippodrome.textContent = "Par hippodrome";
      details.appendChild(titreHippodrome);
      details.appendChild(
        construireSousTableauJSON(modele.roi_par_hippodrome, [
          { libelle: "Hippodrome", cle: "hippodrome_id", carte: nomHippodrome, prefixe: "hippodrome" },
          { libelle: "Courses", cle: "nb_courses" },
          { libelle: "Mises €", cle: "mises", montant: true },
          { libelle: "Gains €", cle: "gains", montant: true },
          { libelle: "ROI %", cle: "roi" },
        ])
      );

      const titrePari = document.createElement("h4");
      titrePari.textContent = "Par type de pari";
      details.appendChild(titrePari);
      details.appendChild(
        construireSousTableauJSON(modele.roi_par_type_pari, [
          { libelle: "Type de pari", cle: "type_pari" },
          { libelle: "Paris", cle: "nb_paris" },
          { libelle: "Mises €", cle: "mises", montant: true },
          { libelle: "Gains €", cle: "gains", montant: true },
          { libelle: "ROI %", cle: "roi" },
          { libelle: "Taux réussite (paris) %", cle: "taux_reussite" },
        ])
      );

      bloc.appendChild(details);
      conteneur.appendChild(bloc);
    }
  } catch (erreur) {
    conteneur.textContent = `Erreur : ${erreur.message}`;
  }
}

// Bloc "Globale" : segmenté par jour de course (retour utilisateur,
// 2026-07-12 : « segmente ce tableau par jour avec une consolidation
// totale »), avec une ligne "Total" consolidée en bas, puis un graphique
// barre (profit du jour) + courbe (profit cumulé) sous le tableau.
const COLONNES_GLOBALE_JOUR = [
  { libelle: "Jour", cle: "jour" },
  { libelle: "Courses", cle: "nb_courses" },
  { libelle: "Jouées", cle: "nb_jouees" },
  { libelle: "Ignorées", cle: "nb_ignorees" },
  { libelle: "Mises €", cle: "mises", montant: true },
  { libelle: "Gains €", cle: "gains", montant: true },
  { libelle: "Profit €", cle: "profit", montant: true },
  { libelle: "ROI %", cle: "roi" },
  { libelle: "Taux réussite (courses) %", cle: "taux_reussite" },
];

function construireLigneGlobale(ligne, colonnes) {
  const tr = document.createElement("tr");
  for (const colonne of colonnes) {
    const cellule = document.createElement("td");
    const brut = ligne[colonne.cle];
    cellule.textContent = colonne.montant ? formaterMontant(brut) : formaterValeur(brut);
    tr.appendChild(cellule);
  }
  return tr;
}

// Graphique barre (profit du jour, vert/rouge) + courbe (profit cumulé) —
// pas de bibliothèque de graphique dans cette app (vanilla JS sans build) :
// SVG construit à la main, même principe que les jauges linéaires d'Accueil
// (positionnement calculé en JS) mais en SVG pour tracer la courbe.
function construireGraphiqueGlobaleJours(jours) {
  // `jours` du plus récent au plus ancien (comme le tableau) : le graphique
  // se lit de gauche à droite dans l'ordre chronologique naturel.
  const joursChrono = [...jours].reverse();
  const largeur = 800;
  const hauteur = 260;
  const marge = { haut: 10, bas: 24, gauche: 55, droite: 10 };
  const largeurUtile = largeur - marge.gauche - marge.droite;
  const hauteurUtile = hauteur - marge.haut - marge.bas;

  let cumul = 0;
  const points = joursChrono.map((j) => {
    cumul += j.profit ?? 0;
    return { jour: j.jour, profit: j.profit ?? 0, cumul };
  });

  const toutesValeurs = points.flatMap((p) => [p.profit, p.cumul]).concat([0]);
  const min = Math.min(...toutesValeurs);
  const max = Math.max(...toutesValeurs);
  const etendue = max - min || 1;
  const echelleY = (valeur) => marge.haut + hauteurUtile * (1 - (valeur - min) / etendue);
  const yZero = echelleY(0);

  const n = points.length;
  const pasX = largeurUtile / n;
  const xCentre = (i) => marge.gauche + pasX * (i + 0.5);
  const largeurBarre = Math.max(2, Math.min(28, pasX * 0.6));

  const svgNS = "http://www.w3.org/2000/svg";
  const svg = document.createElementNS(svgNS, "svg");
  svg.setAttribute("viewBox", `0 0 ${largeur} ${hauteur}`);
  svg.setAttribute("class", "graphique-globale");
  svg.setAttribute("role", "img");
  svg.setAttribute("aria-label", "Profit par jour et profit cumulé");

  const ligneZero = document.createElementNS(svgNS, "line");
  ligneZero.setAttribute("x1", marge.gauche);
  ligneZero.setAttribute("x2", largeur - marge.droite);
  ligneZero.setAttribute("y1", yZero);
  ligneZero.setAttribute("y2", yZero);
  ligneZero.setAttribute("class", "graphique-axe-zero");
  svg.appendChild(ligneZero);

  points.forEach((p, i) => {
    const y0 = echelleY(0);
    const y1 = echelleY(p.profit);
    const rect = document.createElementNS(svgNS, "rect");
    rect.setAttribute("x", xCentre(i) - largeurBarre / 2);
    rect.setAttribute("y", Math.min(y0, y1));
    rect.setAttribute("width", largeurBarre);
    rect.setAttribute("height", Math.max(1, Math.abs(y1 - y0)));
    rect.setAttribute("class", p.profit >= 0 ? "graphique-barre-gain" : "graphique-barre-perte");
    const titre = document.createElementNS(svgNS, "title");
    titre.textContent = `${p.jour} : profit ${formaterMontant(p.profit)} € (cumul ${formaterMontant(p.cumul)} €)`;
    rect.appendChild(titre);
    svg.appendChild(rect);
  });

  const polyligne = document.createElementNS(svgNS, "polyline");
  polyligne.setAttribute("points", points.map((p, i) => `${xCentre(i)},${echelleY(p.cumul)}`).join(" "));
  polyligne.setAttribute("class", "graphique-courbe-cumul");
  svg.appendChild(polyligne);

  return svg;
}

async function chargerGlobale() {
  const conteneurTableau = document.getElementById("section-globale");
  const conteneurGraphique = document.getElementById("graphique-globale-jours");
  try {
    const donnees = await apiFetch("/statistiques/globale/jours");
    conteneurTableau.innerHTML = "";

    const table = document.createElement("table");
    const entete = document.createElement("thead");
    const ligneEntete = document.createElement("tr");
    for (const colonne of COLONNES_GLOBALE_JOUR) {
      const cellule = document.createElement("th");
      cellule.textContent = colonne.libelle;
      ligneEntete.appendChild(cellule);
    }
    entete.appendChild(ligneEntete);
    table.appendChild(entete);

    const corps = document.createElement("tbody");
    if (donnees.jours.length === 0) {
      const ligneVide = document.createElement("tr");
      const cellule = document.createElement("td");
      cellule.colSpan = COLONNES_GLOBALE_JOUR.length;
      cellule.textContent = "Aucune donnée.";
      ligneVide.appendChild(cellule);
      corps.appendChild(ligneVide);
    }
    for (const jour of donnees.jours) {
      corps.appendChild(construireLigneGlobale(jour, COLONNES_GLOBALE_JOUR));
    }
    const ligneTotal = construireLigneGlobale(
      { ...donnees.total, jour: "Total" },
      COLONNES_GLOBALE_JOUR,
    );
    ligneTotal.className = "ligne-total";
    corps.appendChild(ligneTotal);
    table.appendChild(corps);
    conteneurTableau.appendChild(table);

    conteneurGraphique.innerHTML = "";
    if (donnees.jours.length > 0) {
      conteneurGraphique.appendChild(construireGraphiqueGlobaleJours(donnees.jours));
    }
  } catch (erreur) {
    conteneurTableau.textContent = `Erreur : ${erreur.message}`;
  }
}

chargerGlobale();

chargerSectionSimple("/statistiques/scores", "section-scores", [
  { libelle: "Score min", cle: "score_min" },
  { libelle: "Score max", cle: "score_max" },
  { libelle: "Courses", cle: "nb_courses" },
  { libelle: "Gagnantes", cle: "nb_gagnantes" },
  { libelle: "ROI %", cle: "roi" },
  { libelle: "Taux réussite (courses) %", cle: "taux_reussite" },
]);

// `hippodrome_id`/`discipline_id` seuls ne permettent pas de savoir de quel
// hippodrome/discipline il s'agit réellement — retour utilisateur : « remplace
// les chiffres par les noms ». Chargé une fois, réutilisé pour la colonne
// concernée (repli sur l'identifiant brut si l'entrée est absente de la carte).
async function chargerCarteReferentiel(chemin, cleNom) {
  try {
    const items = await apiFetch(chemin);
    return new Map(items.map((item) => [item.id, item[cleNom]]));
  } catch (erreur) {
    return new Map();
  }
}

async function chargerSectionsAvecReferentiels() {
  const nomHippodrome = await chargerCarteReferentiel("/hippodromes", "nom");
  chargerSectionSimple("/statistiques/hippodromes", "section-hippodromes", [
    { libelle: "Hippodrome", cle: "hippodrome_id", carte: nomHippodrome, prefixe: "hippodrome" },
    { libelle: "Courses", cle: "nb_courses" },
    { libelle: "Mises €", cle: "mises", montant: true },
    { libelle: "Gains €", cle: "gains", montant: true },
    { libelle: "Profit €", cle: "profit", montant: true },
    { libelle: "ROI %", cle: "roi" },
  ]);

  const nomDiscipline = await chargerCarteReferentiel("/disciplines", "libelle");
  chargerSectionSimple("/statistiques/disciplines", "section-disciplines", [
    { libelle: "Discipline", cle: "discipline_id", carte: nomDiscipline, prefixe: "discipline" },
    { libelle: "Courses", cle: "nb_courses" },
    { libelle: "Mises €", cle: "mises", montant: true },
    { libelle: "Gains €", cle: "gains", montant: true },
    { libelle: "Profit €", cle: "profit", montant: true },
    { libelle: "ROI %", cle: "roi" },
  ]);
}

chargerSectionsAvecReferentiels();

chargerSectionSimple("/statistiques/paris", "section-paris", [
  { libelle: "Type de pari", cle: "type_pari" },
  { libelle: "Paris", cle: "nb_paris" },
  { libelle: "Mises €", cle: "mises", montant: true },
  { libelle: "Gains €", cle: "gains", montant: true },
  { libelle: "Profit €", cle: "profit", montant: true },
  { libelle: "ROI %", cle: "roi" },
  { libelle: "Taux réussite (paris) %", cle: "taux_reussite" },
]);

chargerModeles();

// -- Déclenchement du rejeu depuis l'interface (retour utilisateur : « on ne
// peut pas lancer pour les jours précédents », « fais des grilles avec
// toutes les familles et leurs poids par défaut, modifiables dans la
// grille ») -----------------------------------------------------------------

// cf. src/algorithms/score.py::PONDERATIONS_PAR_DEFAUT et
// src/algorithms/risque.py::PONDERATIONS_PAR_DEFAUT — mêmes clés, même ordre.
const FAMILLES_SCORE = ["marche", "presse", "forme", "aptitude", "professionnels", "historique", "value", "contexte"];
const FAMILLES_RISQUE = ["marche", "presse", "course", "terrain", "historique", "contexte", "statistiques"];

function construireGrillePoids(familles, poidsActuels) {
  const table = document.createElement("table");
  const entete = document.createElement("thead");
  entete.innerHTML = "<tr><th>Famille</th><th>Poids</th></tr>";
  table.appendChild(entete);

  const corps = document.createElement("tbody");
  for (const famille of familles) {
    const tr = document.createElement("tr");
    const celluleNom = document.createElement("td");
    celluleNom.textContent = famille;
    tr.appendChild(celluleNom);

    const celluleValeur = document.createElement("td");
    const input = document.createElement("input");
    input.type = "number";
    input.step = "0.1";
    input.min = "0";
    input.dataset.famille = famille;
    input.value = poidsActuels[famille] ?? 1.0;
    input.className = "champ-poids";
    celluleValeur.appendChild(input);
    tr.appendChild(celluleValeur);

    corps.appendChild(tr);
  }
  table.appendChild(corps);
  return table;
}

function lireGrillePoids(conteneurId) {
  const poids = {};
  for (const input of document.querySelectorAll(`#${conteneurId} input[data-famille]`)) {
    poids[input.dataset.famille] = parseFloat(input.value) || 0;
  }
  return poids;
}

// Pré-remplit les grilles avec les poids réellement utilisés en production
// (`parametre.poids_score.*`/`poids_risque.*`, cf. Administration) plutôt que
// de deviner — repli sur 1.0 (poids égal, cf. PONDERATIONS_PAR_DEFAUT) si un
// paramètre est absent.
async function chargerGrillesPoids() {
  let poidsScoreActuels = {};
  let poidsRisqueActuels = {};
  try {
    const parametres = await apiFetch("/administration/parametres");
    for (const p of parametres) {
      if (p.cle.startsWith("poids_score.")) poidsScoreActuels[p.cle.slice("poids_score.".length)] = parseFloat(p.valeur);
      if (p.cle.startsWith("poids_risque.")) poidsRisqueActuels[p.cle.slice("poids_risque.".length)] = parseFloat(p.valeur);
    }
  } catch (erreur) {
    // Grilles non bloquantes : repli sur 1.0 partout si les paramètres ne chargent pas.
  }

  const conteneurScore = document.getElementById("grille-poids-score");
  conteneurScore.innerHTML = "";
  conteneurScore.appendChild(construireGrillePoids(FAMILLES_SCORE, poidsScoreActuels));

  const conteneurRisque = document.getElementById("grille-poids-risque");
  conteneurRisque.innerHTML = "";
  conteneurRisque.appendChild(construireGrillePoids(FAMILLES_RISQUE, poidsRisqueActuels));
}

chargerGrillesPoids();

document.getElementById("formulaire-rejeu").addEventListener("submit", async (evenement) => {
  evenement.preventDefault();
  const message = document.getElementById("message-rejeu");
  message.hidden = true;
  message.textContent = "";

  const payload = {
    version_modele: document.getElementById("rejeu-version").value,
    date_debut: document.getElementById("rejeu-date-debut").value,
    date_fin: document.getElementById("rejeu-date-fin").value,
    poids_score: lireGrillePoids("grille-poids-score"),
    poids_risque: lireGrillePoids("grille-poids-risque"),
    commentaire: document.getElementById("rejeu-commentaire").value || null,
  };

  try {
    const stat = await apiFetch("/administration/rejeu", { method: "POST", body: JSON.stringify(payload) });
    message.className = "message-succes";
    message.textContent = `Terminé : ${stat.nb_courses} course(s) rejouée(s), ROI ${formaterValeur(stat.roi)} %.`;
  } catch (erreur) {
    message.className = "message-erreur";
    message.textContent = `Erreur : ${erreur.message}`;
  }
  message.hidden = false;
  await chargerModeles();
});

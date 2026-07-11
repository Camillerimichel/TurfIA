// Page Historique (cf. L018 §8) — recherche transversale sur analyses/paris/ROI.

initialiserEntete();

function formaterValeur(valeur) {
  if (valeur === null || valeur === undefined) return "—";
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
      if (colonne.cle === "course_nom") {
        const lien = document.createElement("a");
        lien.href = `/course.html?id=${ligne.course_id}`;
        lien.textContent = `${ligne.course_numero} — ${ligne.course_nom}`;
        cellule.appendChild(lien);
      } else if (colonne.montant) {
        const brut = ligne[colonne.cle];
        cellule.textContent = brut === null || brut === undefined ? "—" : formaterMontant(brut);
      } else if (colonne.entier) {
        const brut = ligne[colonne.cle];
        cellule.textContent = brut === null || brut === undefined ? "—" : String(Math.round(brut));
      } else {
        cellule.textContent = formaterValeur(ligne[colonne.cle]);
      }
      tr.appendChild(cellule);
    }
    corps.appendChild(tr);
  }
  table.appendChild(corps);
  return table;
}

// cf. src/core/constants.py::DECISIONS — même liste, même ordre.
const TOUTES_DECISIONS = ["Ne pas jouer", "Jeu prudent", "Jeu normal", "Forte opportunité"];

function decisionsSelectionnees() {
  return [...document.querySelectorAll('#filtre-decision input[type="checkbox"]:checked')].map(
    (case_) => case_.value
  );
}

const COLONNES = [
  { libelle: "Date", cle: "date" },
  { libelle: "Hippodrome", cle: "hippodrome_nom" },
  { libelle: "Course", cle: "course_nom" },
  { libelle: "Analysée le", cle: "date_calcul" },
  { libelle: "Décision", cle: "decision" },
  { libelle: "Score", cle: "score_confiance", entier: true },
  { libelle: "Risque", cle: "risque" },
  { libelle: "Type de pari", cle: "type_pari" },
  { libelle: "ROI estimé %", cle: "roi_estime", entier: true },
  { libelle: "ROI réel %", cle: "roi_reel" },
  { libelle: "Mise €", cle: "mise", montant: true },
  { libelle: "Gain réel €", cle: "gains_reel", montant: true },
  { libelle: "Profit réel €", cle: "profit_reel", montant: true },
  { libelle: "Validé", cle: "valide" },
];

async function chargerHippodromes() {
  const select = document.getElementById("filtre-hippodrome");
  try {
    const hippodromes = await apiFetch("/hippodromes");
    for (const hippodrome of hippodromes) {
      const option = document.createElement("option");
      option.value = hippodrome.id;
      option.textContent = hippodrome.nom;
      select.appendChild(option);
    }
  } catch (erreur) {
    // Filtre non bloquant : la recherche reste utilisable sans la liste des hippodromes.
  }
}

async function rechercherHistorique() {
  const conteneur = document.getElementById("section-historique");
  conteneur.textContent = "Chargement…";

  const parametres = new URLSearchParams();
  const dateDebut = document.getElementById("filtre-date-debut").value;
  const dateFin = document.getElementById("filtre-date-fin").value;
  const hippodromeId = document.getElementById("filtre-hippodrome").value;
  const typePari = document.getElementById("filtre-type-pari").value;
  const decisions = decisionsSelectionnees();
  if (decisions.length === 0) {
    // Aucune décision cochée : rien ne peut correspondre, pas la peine d'appeler l'API.
    conteneur.innerHTML = "";
    conteneur.appendChild(construireTableau([], COLONNES));
    return;
  }
  if (dateDebut) parametres.set("date_debut", dateDebut);
  if (dateFin) parametres.set("date_fin", dateFin);
  if (hippodromeId) parametres.set("hippodrome_id", hippodromeId);
  if (typePari) parametres.set("type_pari", typePari);
  // Toutes les décisions cochées = pas de filtrage réel (cf. accueil.js) :
  // ne rien envoyer plutôt que la liste complète, pour rester cohérent avec
  // "aucune sélection" côté API.
  if (decisions.length < TOUTES_DECISIONS.length) {
    for (const decision of decisions) parametres.append("decisions", decision);
  }

  try {
    const lignes = await apiFetch(`/historique?${parametres.toString()}`);
    conteneur.innerHTML = "";
    conteneur.appendChild(construireTableau(lignes, COLONNES));
  } catch (erreur) {
    conteneur.textContent = `Erreur : ${erreur.message}`;
  }
}

document.getElementById("formulaire-filtres").addEventListener("submit", (evenement) => {
  evenement.preventDefault();
  rechercherHistorique();
});

chargerHippodromes();
rechercherHistorique();

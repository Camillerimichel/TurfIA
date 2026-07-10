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
      cellule.textContent = colonne.montant ? formaterMontant(ligne[colonne.cle]) : formaterValeur(ligne[colonne.cle]);
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
    const modeles = await apiFetch("/statistiques/modeles");
    conteneur.innerHTML = "";
    if (modeles.length === 0) {
      conteneur.textContent = "Aucune donnée.";
      return;
    }
    for (const modele of modeles) {
      const bloc = document.createElement("div");
      bloc.className = "bloc-modele";

      const titre = document.createElement("h3");
      titre.textContent = `Version « ${modele.version_modele} »`;
      bloc.appendChild(titre);

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
          { libelle: "Taux réussite %", cle: "taux_reussite" },
        ])
      );

      const titreHippodrome = document.createElement("h4");
      titreHippodrome.textContent = "Par hippodrome";
      details.appendChild(titreHippodrome);
      details.appendChild(
        construireSousTableauJSON(modele.roi_par_hippodrome, [
          { libelle: "Hippodrome", cle: "hippodrome_id" },
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
          { libelle: "Taux réussite %", cle: "taux_reussite" },
        ])
      );

      bloc.appendChild(details);
      conteneur.appendChild(bloc);
    }
  } catch (erreur) {
    conteneur.textContent = `Erreur : ${erreur.message}`;
  }
}

chargerSectionSimple("/statistiques/globale", "section-globale", [
  { libelle: "Date de calcul", cle: "date_calcul" },
  { libelle: "Courses", cle: "nb_courses" },
  { libelle: "Jouées", cle: "nb_jouees" },
  { libelle: "Ignorées", cle: "nb_ignorees" },
  { libelle: "Mises €", cle: "mises", montant: true },
  { libelle: "Gains €", cle: "gains", montant: true },
  { libelle: "Profit €", cle: "profit", montant: true },
  { libelle: "ROI %", cle: "roi" },
  { libelle: "Taux réussite %", cle: "taux_reussite" },
]);

chargerSectionSimple("/statistiques/scores", "section-scores", [
  { libelle: "Score min", cle: "score_min" },
  { libelle: "Score max", cle: "score_max" },
  { libelle: "Courses", cle: "nb_courses" },
  { libelle: "Gagnantes", cle: "nb_gagnantes" },
  { libelle: "ROI %", cle: "roi" },
  { libelle: "Taux réussite %", cle: "taux_reussite" },
]);

chargerSectionSimple("/statistiques/hippodromes", "section-hippodromes", [
  { libelle: "Hippodrome", cle: "hippodrome_id" },
  { libelle: "Courses", cle: "nb_courses" },
  { libelle: "Mises €", cle: "mises", montant: true },
  { libelle: "Gains €", cle: "gains", montant: true },
  { libelle: "Profit €", cle: "profit", montant: true },
  { libelle: "ROI %", cle: "roi" },
]);

chargerSectionSimple("/statistiques/disciplines", "section-disciplines", [
  { libelle: "Discipline", cle: "discipline_id" },
  { libelle: "Courses", cle: "nb_courses" },
  { libelle: "Mises €", cle: "mises", montant: true },
  { libelle: "Gains €", cle: "gains", montant: true },
  { libelle: "Profit €", cle: "profit", montant: true },
  { libelle: "ROI %", cle: "roi" },
]);

chargerSectionSimple("/statistiques/paris", "section-paris", [
  { libelle: "Type de pari", cle: "type_pari" },
  { libelle: "Paris", cle: "nb_paris" },
  { libelle: "Mises €", cle: "mises", montant: true },
  { libelle: "Gains €", cle: "gains", montant: true },
  { libelle: "Profit €", cle: "profit", montant: true },
  { libelle: "ROI %", cle: "roi" },
  { libelle: "Taux réussite %", cle: "taux_reussite" },
]);

chargerModeles();

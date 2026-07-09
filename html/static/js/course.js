// Fiche course (cf. L018 §6-7) — infos, partants, résultats, déclenchement et
// consultation des analyses.

initialiserEntete();

const idCourse = new URLSearchParams(window.location.search).get("id");

function derniereCote(cotes) {
  if (!cotes || cotes.length === 0) return null;
  return [...cotes].sort((a, b) => new Date(b.date_maj) - new Date(a.date_maj))[0];
}

async function nomOuNull(chemin) {
  try {
    return await apiFetch(chemin);
  } catch (erreur) {
    return null;
  }
}

async function chargerCourse() {
  const course = await apiFetch(`/courses/${idCourse}`);
  document.getElementById("titre-course").textContent = `Course ${course.numero} — ${course.nom}`;
  const infos = document.getElementById("infos-course");
  infos.innerHTML = "";
  const details = [
    ["Heure de départ", course.heure_depart ?? "n/a"],
    ["Allocation", course.allocation !== null ? `${course.allocation} €` : "n/a"],
    ["Nombre de partants annoncé", course.nb_partants ?? "n/a"],
    ["Quinté+", course.quinte ? "Oui" : "Non"],
  ];
  for (const [libelle, valeur] of details) {
    const p = document.createElement("p");
    p.textContent = `${libelle} : ${valeur}`;
    infos.appendChild(p);
  }
  return course;
}

async function chargerPartants() {
  const corpsTableau = document.querySelector("#tableau-partants tbody");
  corpsTableau.innerHTML = "";
  const partants = await apiFetch(`/courses/${idCourse}/partants`);

  for (const partant of partants) {
    const [cheval, jockey, entraineur, cotes] = await Promise.all([
      nomOuNull(`/chevaux/${partant.cheval_id}`),
      partant.jockey_id ? nomOuNull(`/jockeys/${partant.jockey_id}`) : Promise.resolve(null),
      partant.entraineur_id ? nomOuNull(`/entraineurs/${partant.entraineur_id}`) : Promise.resolve(null),
      apiFetch(`/partants/${partant.id}/cotes`).catch(() => []),
    ]);
    const cote = derniereCote(cotes);

    const ligne = document.createElement("tr");
    const cellules = [
      partant.numero,
      cheval ? cheval.nom : `#${partant.cheval_id}`,
      jockey ? `${jockey.prenom ?? ""} ${jockey.nom}`.trim() : "—",
      entraineur ? `${entraineur.prenom ?? ""} ${entraineur.nom}`.trim() : "—",
      cote ? `${cote.cote} (${cote.operateur})` : "—",
      partant.non_partant ? "Oui" : "Non",
    ];
    for (const valeur of cellules) {
      const cellule = document.createElement("td");
      cellule.textContent = valeur;
      ligne.appendChild(cellule);
    }
    corpsTableau.appendChild(ligne);
  }
}

async function chargerResultats() {
  const resultats = await apiFetch(`/courses/${idCourse}/resultats`);
  if (resultats.length === 0) return;
  document.getElementById("section-resultats").hidden = false;
  const corpsTableau = document.querySelector("#tableau-resultats tbody");
  corpsTableau.innerHTML = "";
  const tries = [...resultats].sort((a, b) => (a.classement ?? 999) - (b.classement ?? 999));
  for (const resultat of tries) {
    const ligne = document.createElement("tr");
    const cellules = [
      resultat.disqualification ? "Disqualifié" : (resultat.classement ?? "—"),
      resultat.partant_id,
      resultat.temps ?? "—",
      resultat.ecart ?? "—",
    ];
    for (const valeur of cellules) {
      const cellule = document.createElement("td");
      cellule.textContent = valeur;
      ligne.appendChild(cellule);
    }
    corpsTableau.appendChild(ligne);
  }
}

function formaterDetailAnalyse(detail) {
  const conteneur = document.createElement("div");
  const titre = document.createElement("h3");
  titre.textContent = `Analyse #${detail.analyse.id} — décision : ${detail.analyse.decision ?? "n/a"}`;
  conteneur.appendChild(titre);

  const resume = document.createElement("p");
  resume.textContent =
    `Score de confiance : ${detail.analyse.score_confiance ?? "n/a"} — ` +
    `Risque : ${detail.analyse.risque ?? "n/a"} — ` +
    `ROI théorique : ${detail.analyse.roi_theorique ?? "n/a"} — ` +
    `Budget : ${detail.analyse.budget} €`;
  conteneur.appendChild(resume);

  const tableauPartants = document.createElement("table");
  tableauPartants.innerHTML = "<thead><tr><th>Rang</th><th>Partant</th><th>Catégorie</th><th>Confiance</th></tr></thead>";
  const corps = document.createElement("tbody");
  for (const p of detail.partants) {
    const ligne = document.createElement("tr");
    for (const valeur of [p.rang, p.partant_id, p.categorie ?? "—", p.confiance ?? "—"]) {
      const cellule = document.createElement("td");
      cellule.textContent = valeur;
      ligne.appendChild(cellule);
    }
    corps.appendChild(ligne);
  }
  tableauPartants.appendChild(corps);
  conteneur.appendChild(tableauPartants);

  if (detail.paris.length > 0) {
    const titreParis = document.createElement("h4");
    titreParis.textContent = "Paris";
    conteneur.appendChild(titreParis);
    const tableauParis = document.createElement("table");
    tableauParis.innerHTML = "<thead><tr><th>Type</th><th>Mise</th><th>ROI estimé</th></tr></thead>";
    const corpsParis = document.createElement("tbody");
    for (const pari of detail.paris) {
      const ligne = document.createElement("tr");
      for (const valeur of [pari.type_pari, `${pari.mise} €`, pari.roi_estime ?? "—"]) {
        const cellule = document.createElement("td");
        cellule.textContent = valeur;
        ligne.appendChild(cellule);
      }
      corpsParis.appendChild(ligne);
    }
    tableauParis.appendChild(corpsParis);
    conteneur.appendChild(tableauParis);
  }
  return conteneur;
}

async function chargerAnalyses() {
  const conteneur = document.getElementById("liste-analyses");
  const detailConteneur = document.getElementById("detail-analyse");
  detailConteneur.innerHTML = "";
  const analyses = await apiFetch(`/courses/${idCourse}/analyses`);
  if (analyses.length === 0) {
    conteneur.textContent = "Aucune analyse pour cette course.";
    return;
  }
  conteneur.innerHTML = "";
  const liste = document.createElement("ul");
  for (const analyse of analyses) {
    const item = document.createElement("li");
    const lien = document.createElement("a");
    lien.href = "#";
    lien.textContent = `Analyse #${analyse.id} (v${analyse.version}) — ${analyse.decision ?? "n/a"}`;
    lien.addEventListener("click", async (evenement) => {
      evenement.preventDefault();
      const detail = await apiFetch(`/analyses/${analyse.id}`);
      detailConteneur.innerHTML = "";
      detailConteneur.appendChild(formaterDetailAnalyse(detail));
    });
    item.appendChild(lien);
    liste.appendChild(item);
  }
  conteneur.appendChild(liste);
}

document.getElementById("formulaire-analyse").addEventListener("submit", async (evenement) => {
  evenement.preventDefault();
  const message = document.getElementById("message-analyse");
  message.hidden = true;

  if (!window.confirm("Déclencher une nouvelle analyse pour cette course ?")) {
    return;
  }

  const payload = {
    mise_reference: parseFloat(document.getElementById("mise-reference").value),
    budget_precedent: parseFloat(document.getElementById("budget-precedent").value),
    perte_precedente: document.getElementById("perte-precedente").checked,
  };

  try {
    const detail = await apiFetch(`/courses/${idCourse}/analyses/auto`, {
      method: "POST",
      body: JSON.stringify(payload),
    });
    message.textContent = `Analyse #${detail.analyse.id} créée — décision : ${detail.analyse.decision ?? "n/a"}.`;
    message.hidden = false;
    await chargerAnalyses();
  } catch (erreur) {
    message.textContent = `Erreur : ${erreur.message}`;
    message.hidden = false;
  }
});

chargerCourse();
chargerPartants();
chargerResultats();
chargerAnalyses();

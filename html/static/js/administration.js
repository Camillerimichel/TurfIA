// Page Administration (cf. L018 §10) — journaux, automatisations, sauvegardes,
// versions, paramètres, supervision. Réservée au rôle Administrateur (RBAC déjà
// appliqué côté API ; ici on affiche juste le résultat/erreur 403 le cas échéant).

initialiserEntete();

function formaterValeur(valeur) {
  if (valeur === null || valeur === undefined) return "—";
  if (typeof valeur === "boolean") return valeur ? "Oui" : "Non";
  if (typeof valeur === "number") return Number.isInteger(valeur) ? valeur : valeur.toFixed(2);
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
      cellule.textContent = formaterValeur(ligne[colonne.cle]);
      tr.appendChild(cellule);
    }
    corps.appendChild(tr);
  }
  table.appendChild(corps);
  return table;
}

async function chargerSection(chemin, idSection, colonnes) {
  const conteneur = document.getElementById(idSection);
  try {
    const lignes = await apiFetch(chemin);
    conteneur.innerHTML = "";
    conteneur.appendChild(construireTableau(lignes, colonnes));
  } catch (erreur) {
    conteneur.textContent = `Erreur : ${erreur.message}`;
  }
}

// -- Supervision ----------------------------------------------------------------

async function chargerSupervision() {
  const conteneur = document.getElementById("section-supervision");
  try {
    const etat = await apiFetch("/administration/supervision");
    conteneur.innerHTML = "";
    const lignes = [
      ["Connexion base de données", etat.base_de_donnees_ok ? "OK" : "En échec"],
      ["Latence base de données", etat.latence_db_ms !== null ? `${etat.latence_db_ms.toFixed(1)} ms` : "n/a"],
      ["Espace disque disponible", `${(etat.espace_disque_disponible_octets / 1e9).toFixed(2)} Go`],
      ["Tâches en échec (24h)", etat.taches_en_echec_24h],
      ["Démarré depuis", `${(etat.uptime_secondes / 3600).toFixed(1)} h`],
    ];
    for (const [libelle, valeur] of lignes) {
      const p = document.createElement("p");
      p.textContent = `${libelle} : ${valeur}`;
      conteneur.appendChild(p);
    }
  } catch (erreur) {
    conteneur.textContent = `Erreur : ${erreur.message}`;
  }
}

// -- Automatisations --------------------------------------------------------------

const COLONNES_TACHES = [
  { libelle: "Nom", cle: "nom" },
  { libelle: "Début", cle: "debut" },
  { libelle: "Durée (ms)", cle: "duree_ms" },
  { libelle: "Statut", cle: "statut" },
  { libelle: "Commentaire", cle: "commentaire" },
];

function chargerTaches() {
  return chargerSection("/administration/automatisations", "section-taches", COLONNES_TACHES);
}

const LIBELLES_RESULTAT_AUTOMATISATION = {
  nb_reunions: "Réunions importées",
  nb_courses: "Courses importées",
  nb_partants: "Partants importés",
  nb_erreurs: "Erreurs",
  nb_controles_roi: "Contrôles ROI calculés",
};

function construireResumeAutomatisation(resultat) {
  const conteneur = document.createElement("div");

  const titre = document.createElement("p");
  titre.textContent = "Terminé.";
  conteneur.appendChild(titre);

  for (const [cle, valeur] of Object.entries(resultat)) {
    if (cle === "erreurs" || cle === "tables") continue; // rendus à part ci-dessous
    const p = document.createElement("p");
    p.textContent = `${LIBELLES_RESULTAT_AUTOMATISATION[cle] ?? cle} : ${formaterValeur(valeur)}`;
    conteneur.appendChild(p);
  }

  if (resultat.tables) {
    const p = document.createElement("p");
    p.textContent = "Tables recalculées :";
    conteneur.appendChild(p);
    const liste = document.createElement("ul");
    liste.className = "liste-paris";
    for (const [table, nb] of Object.entries(resultat.tables)) {
      const li = document.createElement("li");
      li.textContent = `${table} : ${nb} ligne(s)`;
      liste.appendChild(li);
    }
    conteneur.appendChild(liste);
  }

  if (resultat.erreurs && resultat.erreurs.length > 0) {
    const p = document.createElement("p");
    p.textContent = `Erreurs (${resultat.erreurs.length}) :`;
    conteneur.appendChild(p);
    const liste = document.createElement("ul");
    liste.className = "liste-paris";
    for (const erreur of resultat.erreurs) {
      const li = document.createElement("li");
      // Selon l'automatisation : une chaîne (collecte) ou {course_id, message} (analyse-jour).
      li.textContent = typeof erreur === "string" ? erreur : `Course ${erreur.course_id} : ${erreur.message}`;
      liste.appendChild(li);
    }
    conteneur.appendChild(liste);
  }

  return conteneur;
}

async function declencherAutomatisation(chemin, libelleConfirmation) {
  const message = document.getElementById("message-automatisation");
  message.hidden = true;
  message.innerHTML = "";
  if (!window.confirm(libelleConfirmation)) return;

  try {
    const resultat = await apiFetch(chemin, { method: "POST" });
    message.className = "message-succes";
    message.appendChild(construireResumeAutomatisation(resultat));
  } catch (erreur) {
    message.className = "message-erreur";
    message.textContent = `Erreur : ${erreur.message}`;
  }
  message.hidden = false;
  await chargerTaches();
}

document.getElementById("bouton-collecte").addEventListener("click", () =>
  declencherAutomatisation("/administration/automatisations/collecte", "Collecter le programme du jour ?")
);
document.getElementById("bouton-analyse-jour").addEventListener("click", () =>
  declencherAutomatisation("/administration/automatisations/analyse-jour", "Analyser toutes les courses du jour ?")
);
document.getElementById("bouton-statistiques").addEventListener("click", () =>
  declencherAutomatisation("/administration/automatisations/statistiques", "Recalculer les statistiques ?")
);

// -- Sauvegardes ------------------------------------------------------------------

const COLONNES_SAUVEGARDES = [
  { libelle: "Début", cle: "debut" },
  { libelle: "Durée (ms)", cle: "duree_ms" },
  { libelle: "Statut", cle: "statut" },
  { libelle: "Commentaire", cle: "commentaire" },
];

function chargerSauvegardes() {
  return chargerSection("/administration/sauvegardes", "section-sauvegardes", COLONNES_SAUVEGARDES);
}

document.getElementById("bouton-sauvegarde").addEventListener("click", async () => {
  const message = document.getElementById("message-sauvegarde");
  message.hidden = true;
  if (!window.confirm("Lancer une sauvegarde de la base maintenant ?")) return;

  try {
    const tache = await apiFetch("/administration/sauvegardes", { method: "POST" });
    message.className = "message-succes";
    message.textContent = `Sauvegarde ${tache.statut} — ${tache.commentaire ?? ""}`;
  } catch (erreur) {
    message.className = "message-erreur";
    message.textContent = `Erreur : ${erreur.message}`;
  }
  message.hidden = false;
  await chargerSauvegardes();
});

// -- Versions -----------------------------------------------------------------------

function chargerVersions() {
  return chargerSection("/administration/versions", "section-versions", [
    { libelle: "Version", cle: "version" },
    { libelle: "Commit", cle: "commit_git" },
    { libelle: "Branche", cle: "branche" },
    { libelle: "Publiée le", cle: "date_publication" },
    { libelle: "Commentaire", cle: "commentaire" },
  ]);
}

// -- Paramètres -----------------------------------------------------------------------

async function chargerParametres() {
  const conteneur = document.getElementById("section-parametres");
  try {
    const parametres = await apiFetch("/administration/parametres");
    conteneur.innerHTML = "";
    const table = document.createElement("table");
    table.innerHTML = "<thead><tr><th>Clé</th><th>Valeur</th><th>Description</th><th></th></tr></thead>";
    const corps = document.createElement("tbody");
    for (const parametre of parametres) {
      const tr = document.createElement("tr");

      const celluleCle = document.createElement("td");
      celluleCle.textContent = parametre.cle;
      tr.appendChild(celluleCle);

      const celluleValeur = document.createElement("td");
      const champ = document.createElement("input");
      champ.type = "text";
      champ.value = parametre.valeur;
      celluleValeur.appendChild(champ);
      tr.appendChild(celluleValeur);

      const celluleDescription = document.createElement("td");
      celluleDescription.textContent = parametre.description ?? "";
      tr.appendChild(celluleDescription);

      const celluleAction = document.createElement("td");
      const bouton = document.createElement("button");
      bouton.type = "button";
      bouton.textContent = "Enregistrer";
      bouton.addEventListener("click", async () => {
        try {
          await apiFetch(`/administration/parametres/${encodeURIComponent(parametre.cle)}`, {
            method: "PATCH",
            body: JSON.stringify({ valeur: champ.value }),
          });
          bouton.textContent = "Enregistré ✓";
          setTimeout(() => (bouton.textContent = "Enregistrer"), 2000);
        } catch (erreur) {
          window.alert(`Erreur : ${erreur.message}`);
        }
      });
      celluleAction.appendChild(bouton);
      tr.appendChild(celluleAction);

      corps.appendChild(tr);
    }
    table.appendChild(corps);
    conteneur.appendChild(table);
  } catch (erreur) {
    conteneur.textContent = `Erreur : ${erreur.message}`;
  }
}

// -- Journaux -----------------------------------------------------------------------

function chargerJournaux() {
  const niveau = document.getElementById("filtre-niveau").value;
  const composant = document.getElementById("filtre-composant").value;
  const parametres = new URLSearchParams();
  if (niveau) parametres.set("niveau", niveau);
  if (composant) parametres.set("composant", composant);
  return chargerSection(`/administration/journaux?${parametres.toString()}`, "section-journaux", [
    { libelle: "Date", cle: "date_evenement" },
    { libelle: "Niveau", cle: "niveau" },
    { libelle: "Composant", cle: "composant" },
    { libelle: "Message", cle: "message" },
  ]);
}

document.getElementById("formulaire-journaux").addEventListener("submit", (evenement) => {
  evenement.preventDefault();
  chargerJournaux();
});

chargerSupervision();
chargerTaches();
chargerSauvegardes();
chargerVersions();
chargerParametres();
chargerJournaux();

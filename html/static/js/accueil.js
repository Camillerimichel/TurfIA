// Page Accueil (cf. L018 §5) — réunions du jour, paris proposés par la
// dernière analyse de chaque course, et ROI global. Périmètre volontairement
// réduit pour ce premier incrément : pas de widgets « tâches automatiques »/
// « santé du système » (aucune automatisation planifiée construite, cf.
// PROJECT_STATE.md).

initialiserEntete();

function formaterDate(date) {
  return date.toISOString().slice(0, 10);
}

// -- Jauges du bloc ROI global -----------------------------------------------
// Retour utilisateur : ROI en jauge divergente [-100 %, +100 %] centrée sur
// 0 %, taux de réussite en jauge linéaire [0 %, 100 %] (même formalisme),
// nombre de courses en jauge sur le total analysé avec le nombre jouées en
// remplissage — le tout sur une seule ligne.

function construireBlocJauge(titre, piste) {
  const bloc = document.createElement("div");
  bloc.className = "bloc-jauge";
  const titreDiv = document.createElement("div");
  titreDiv.className = "bloc-jauge-titre";
  titreDiv.textContent = titre;
  bloc.appendChild(titreDiv);
  bloc.appendChild(piste);
  return bloc;
}

function construireRemplissageJauge(gauche, largeur, couleur) {
  const remplissage = document.createElement("div");
  remplissage.className = "jauge-lineaire-remplissage";
  remplissage.style.left = `${gauche}%`;
  remplissage.style.width = `${largeur}%`;
  remplissage.style.backgroundColor = couleur;
  return remplissage;
}

// ROI : remplissage depuis le centre (0 %) vers la valeur, pas depuis le bord
// gauche (contrairement au taux de réussite) — rouge pour un ROI négatif,
// vert pour un ROI positif.
function construireJaugeRoi(roi) {
  const piste = document.createElement("div");
  piste.className = "jauge-lineaire-piste";

  const centre = document.createElement("div");
  centre.className = "jauge-lineaire-centre";
  piste.appendChild(centre);

  if (typeof roi === "number") {
    const borne = Math.max(-100, Math.min(100, roi));
    const position = ((borne + 100) / 200) * 100; // 0-100 % depuis la gauche, 50 % = 0
    if (borne >= 0) {
      piste.appendChild(construireRemplissageJauge(50, position - 50, "var(--couleur-accent)"));
    } else {
      piste.appendChild(construireRemplissageJauge(position, 50 - position, "var(--couleur-erreur)"));
    }
  }

  return construireBlocJauge(`ROI : ${typeof roi === "number" ? roi.toFixed(2) + " %" : "n/a"}`, piste);
}

function construireJaugeTauxReussite(taux) {
  const piste = document.createElement("div");
  piste.className = "jauge-lineaire-piste";

  if (typeof taux === "number") {
    const borne = Math.max(0, Math.min(100, taux));
    piste.appendChild(construireRemplissageJauge(0, borne, "var(--couleur-accent)"));
  }

  return construireBlocJauge(
    `Taux de réussite : ${typeof taux === "number" ? taux.toFixed(2) + " %" : "n/a"}`,
    piste
  );
}

// Échelle pleine = nombre total de courses analysées ; remplissage = nombre
// de courses jouées parmi elles.
function construireJaugeCourses(nbCourses, nbJouees) {
  const piste = document.createElement("div");
  piste.className = "jauge-lineaire-piste";

  if (nbCourses > 0) {
    const ratio = Math.max(0, Math.min(100, (nbJouees / nbCourses) * 100));
    piste.appendChild(construireRemplissageJauge(0, ratio, "#3a5a7a"));
  }

  return construireBlocJauge(`${nbJouees} jouée(s) / ${nbCourses} analysée(s)`, piste);
}

// Échelle pleine = mises (argent misé), remplissage = gains (argent
// récupéré) — même principe numérateur/dénominateur que la jauge Courses.
// Vert si gains >= mises (au moins couvertes), rouge sinon ; remplissage
// borné à 100 % pour l'affichage (la valeur exacte reste dans le libellé,
// même principe que le bornage de la jauge ROI).
function construireJaugeGains(mises, gains) {
  const piste = document.createElement("div");
  piste.className = "jauge-lineaire-piste";

  if (typeof mises === "number" && mises > 0 && typeof gains === "number") {
    const ratio = Math.max(0, Math.min(100, (gains / mises) * 100));
    const couleur = gains >= mises ? "var(--couleur-accent)" : "var(--couleur-erreur)";
    piste.appendChild(construireRemplissageJauge(0, ratio, couleur));
  }

  return construireBlocJauge(`Gains : ${formaterMontant(gains)} € (mises ${formaterMontant(mises)} €)`, piste);
}

async function chargerRoiGlobal() {
  const conteneur = document.getElementById("widget-roi-global");
  try {
    const lignes = await apiFetch("/statistiques/globale");
    conteneur.innerHTML = "";
    if (lignes.length === 0) {
      const vide = document.createElement("p");
      vide.textContent = "Aucune statistique calculée pour l'instant.";
      conteneur.appendChild(vide);
    } else {
      const derniere = [...lignes].sort((a, b) => new Date(b.date_calcul) - new Date(a.date_calcul))[0];
      const ligneJauges = document.createElement("div");
      ligneJauges.className = "blocs-jauges-ligne";
      ligneJauges.appendChild(construireJaugeRoi(derniere.roi));
      ligneJauges.appendChild(construireJaugeTauxReussite(derniere.taux_reussite));
      ligneJauges.appendChild(construireJaugeCourses(derniere.nb_courses, derniere.nb_jouees));
      ligneJauges.appendChild(construireJaugeGains(derniere.mises, derniere.gains));
      conteneur.appendChild(ligneJauges);

      const miseAJour = document.createElement("p");
      miseAJour.className = "note";
      miseAJour.textContent = `Dernière mise à jour : ${derniere.date_calcul ? formaterDateHeure(derniere.date_calcul) : "n/a"}`;
      conteneur.appendChild(miseAJour);
    }
  } catch (erreur) {
    conteneur.textContent = `Erreur : ${erreur.message}`;
  }
}

// Paris déjà engagés (budget > 0) sur des courses pas encore parties — retour
// utilisateur : « il faut afficher la liste des paris en cours à surveiller
// avant leur course, avec un lien vers la course ». Bloc accordéon séparé du
// ROI global (celui-ci doit rester visible en permanence, pas ce bloc).
async function chargerParisEnCours() {
  const conteneur = document.getElementById("widget-paris-en-cours");
  let lignes;
  try {
    lignes = await apiFetch("/historique/paris-en-cours");
  } catch (erreur) {
    conteneur.textContent = `Erreur (paris en cours) : ${erreur.message}`;
    return;
  }

  conteneur.innerHTML = "";

  if (lignes.length === 0) {
    const vide = document.createElement("p");
    vide.className = "note";
    vide.textContent = "Aucun pari en attente sur une course à venir.";
    conteneur.appendChild(vide);
    return;
  }

  for (const ligne of lignes) {
    const bouton = document.createElement("a");
    bouton.className = "bouton-pari-en-cours";
    bouton.href = `/course.html?id=${ligne.course_id}`;

    const titreLigne = document.createElement("div");
    titreLigne.className = "bouton-pari-en-cours-titre";
    titreLigne.textContent = `C${ligne.course_numero} — ${ligne.course_nom} (${ligne.hippodrome_nom})`;
    bouton.appendChild(titreLigne);

    const infos = document.createElement("div");
    infos.className = "bouton-pari-en-cours-infos";
    if (ligne.heure_depart) {
      infos.appendChild(construireBadgeDepart(ligne.heure_depart));
    }
    // Le jeu actuel choisi (décision) juste après la mise (budget), pas avant.
    infos.appendChild(construireBadgeBudget(ligne.budget));
    infos.appendChild(construireBadgeJeu(ligne.decision, ligne.score_confiance));
    bouton.appendChild(infos);

    conteneur.appendChild(bouton);
  }
}

// -- Filtres --------------------------------------------------------------------

async function chargerHippodromes() {
  const select = document.getElementById("filtre-hippodrome-accueil");
  try {
    const hippodromes = await apiFetch("/hippodromes");
    for (const hippodrome of hippodromes) {
      const option = document.createElement("option");
      option.value = hippodrome.id;
      option.textContent = hippodrome.nom;
      select.appendChild(option);
    }
  } catch (erreur) {
    // Filtre non bloquant : la liste des réunions reste utilisable sans la liste des hippodromes.
  }
}

// cf. src/core/constants.py::DECISIONS — même liste, même ordre.
const TOUTES_DECISIONS = ["Ne pas jouer", "Jeu prudent", "Jeu normal", "Forte opportunité"];
const MARGE_COURSES_IMMINENTES_MINUTES = 60;

function decisionsSelectionnees() {
  return [...document.querySelectorAll('#filtre-decision-accueil input[type="checkbox"]:checked')].map(
    (case_) => case_.value
  );
}

// Toutes les décisions cochées = pas de filtrage réel -> tout affiché, y
// compris les courses pas encore analysées (aucune décision). Dès qu'au moins
// une décision est décochée, une course sans décision ne correspond à aucun
// choix et est donc exclue.
function decisionCorrespondAuFiltre(decision, decisions) {
  if (decisions.length === TOUTES_DECISIONS.length) return true;
  if (decision == null) return false;
  return decisions.includes(decision);
}

function departImminent(heureDepartIso) {
  if (!heureDepartIso) return false;
  const minutesRestantes = (new Date(heureDepartIso) - new Date()) / 60000;
  return minutesRestantes > 0 && minutesRestantes <= MARGE_COURSES_IMMINENTES_MINUTES;
}

let filtreImminentActif = false;

// Dernière analyse d'une course (version la plus élevée = la plus récente,
// cf. `analyses.version` Pré/Finale) et ses paris — `null` si pas encore
// analysée.
async function chargerDerniereAnalyse(courseId) {
  const analyses = await apiFetch(`/courses/${courseId}/analyses`);
  if (analyses.length === 0) return null;
  const derniere = [...analyses].sort((a, b) => b.version - a.version)[0];
  return apiFetch(`/analyses/${derniere.id}`);
}

function construireBlocParis(detail) {
  const bloc = document.createElement("div");
  bloc.className = "bloc-paris";

  const entete = document.createElement("p");
  entete.textContent =
    `Décision : ${detail.analyse.decision ?? "n/a"} — ` +
    `score ${detail.analyse.score_confiance ?? "n/a"} — budget ${formaterMontant(detail.analyse.budget)} €`;
  bloc.appendChild(entete);

  const miseAJour = document.createElement("p");
  miseAJour.className = "note";
  miseAJour.textContent = `Analysée le : ${detail.analyse.date_calcul ? formaterDateHeure(detail.analyse.date_calcul) : "n/a"}`;
  bloc.appendChild(miseAJour);

  if (detail.paris.length === 0) {
    const vide = document.createElement("p");
    vide.textContent = "Aucun pari proposé (budget nul ou aucune catégorie constructible).";
    bloc.appendChild(vide);
    return bloc;
  }

  const liste = document.createElement("ul");
  liste.className = "liste-paris";
  for (const pari of detail.paris) {
    const item = document.createElement("li");
    const selection = pari.combinaison_lisible ?? pari.combinaison ?? "—";
    item.textContent = `${pari.type_pari} — ${selection} — mise ${formaterMontant(pari.mise)} €`;

    // Un Quinté Flexi joue plusieurs combinaisons de 5 chevaux à la fois (cf.
    // L031.6 §5) — le pool de chevaux seul ne montre pas les tickets réellement joués.
    if (pari.sous_combinaisons) {
      const sousListe = document.createElement("ul");
      sousListe.className = "liste-paris";
      for (const combinaison of pari.sous_combinaisons) {
        const sousItem = document.createElement("li");
        sousItem.textContent = `${combinaison} — ${formaterMontant(pari.mise_par_combinaison)} €`;
        sousListe.appendChild(sousItem);
      }
      item.appendChild(sousListe);
    }

    liste.appendChild(item);
  }
  bloc.appendChild(liste);
  return bloc;
}

async function chargerReunions(dateJour) {
  const conteneur = document.getElementById("liste-reunions");
  conteneur.textContent = "Chargement…";
  const hippodromeId = document.getElementById("filtre-hippodrome-accueil").value;
  const decisions = decisionsSelectionnees();
  try {
    const parametres = new URLSearchParams({ date: dateJour });
    if (hippodromeId) parametres.set("hippodrome_id", hippodromeId);
    const reunions = await apiFetch(`/reunions?${parametres.toString()}`);
    if (reunions.length === 0) {
      conteneur.textContent = "Aucune réunion à cette date.";
      return;
    }
    conteneur.innerHTML = "";
    let nbReunionsAffichees = 0;
    for (const reunion of reunions) {
      const bloc = document.createElement("div");
      bloc.className = "bloc-reunion";
      const titre = document.createElement("h3");
      titre.textContent = `R${reunion.numero} — ${reunion.hippodrome_nom ?? `hippodrome #${reunion.hippodrome_id}`} (${reunion.statut})`;
      bloc.appendChild(titre);

      let nbCoursesAffichees = 0;
      let erreurReunion = false;
      try {
        const courses = await apiFetch(`/reunions/${reunion.id}/courses`);
        for (const course of courses) {
          if (filtreImminentActif && !departImminent(course.heure_depart)) continue;

          let decision = null;
          let contenuCourse;
          try {
            const detail = await chargerDerniereAnalyse(course.id);
            decision = detail ? detail.analyse.decision : null;
            if (!decisionCorrespondAuFiltre(decision, decisions)) continue;
            contenuCourse = detail
              ? construireBlocParis(detail)
              : (() => {
                  const nonAnalysee = document.createElement("p");
                  nonAnalysee.className = "note";
                  nonAnalysee.textContent = "Pas encore analysée — cliquer sur la course pour lancer l'analyse.";
                  return nonAnalysee;
                })();
          } catch (erreur) {
            const erreurParis = document.createElement("p");
            erreurParis.textContent = `Erreur paris : ${erreur.message}`;
            contenuCourse = erreurParis;
          }

          const blocCourse = document.createElement("div");
          blocCourse.className = "bloc-course";
          const titreCourse = document.createElement("h4");
          const lien = document.createElement("a");
          lien.href = `/course.html?id=${course.id}`;
          lien.textContent = `C${course.numero} — ${course.nom}`;
          titreCourse.appendChild(lien);
          if (course.heure_depart) {
            titreCourse.appendChild(document.createTextNode(" — "));
            titreCourse.appendChild(construireBadgeDepart(course.heure_depart));
          }
          blocCourse.appendChild(titreCourse);
          blocCourse.appendChild(contenuCourse);

          bloc.appendChild(blocCourse);
          nbCoursesAffichees += 1;
        }
      } catch (erreur) {
        const erreurCourses = document.createElement("p");
        erreurCourses.textContent = `Erreur : ${erreur.message}`;
        bloc.appendChild(erreurCourses);
        erreurReunion = true;
      }

      // Une réunion sans aucune course correspondant au filtre décision est
      // masquée entièrement (pas de bloc "R1 — hippodrome" vide) — sauf en cas
      // d'erreur réelle, toujours affichée.
      if (nbCoursesAffichees > 0 || erreurReunion) {
        conteneur.appendChild(bloc);
        nbReunionsAffichees += 1;
      }
    }
    if (nbReunionsAffichees === 0) {
      conteneur.textContent = "Aucune course ne correspond à ce filtre.";
    }
  } catch (erreur) {
    conteneur.textContent = `Erreur : ${erreur.message}`;
  }
}

// Pas de bouton de soumission (filtres appliqués au `change`) — évite qu'une
// touche Entrée dans un des champs ne recharge la page (soumission implicite).
document.getElementById("formulaire-filtres-accueil").addEventListener("submit", (evenement) => evenement.preventDefault());

const selecteurDate = document.getElementById("selecteur-date");
const boutonCoursesImminentes = document.getElementById("bouton-courses-imminentes");

function desactiverFiltreImminent() {
  filtreImminentActif = false;
  boutonCoursesImminentes.classList.remove("actif");
}

selecteurDate.value = formaterDate(new Date());
selecteurDate.addEventListener("change", () => {
  desactiverFiltreImminent();
  chargerReunions(selecteurDate.value);
});
document.getElementById("filtre-hippodrome-accueil").addEventListener("change", () => {
  desactiverFiltreImminent();
  chargerReunions(selecteurDate.value);
});
document.getElementById("filtre-decision-accueil").addEventListener("change", () => {
  desactiverFiltreImminent();
  chargerReunions(selecteurDate.value);
});

// Raccourci : "tout sauf Ne pas jouer" + départ dans l'heure qui suit — force
// la date du jour et les décisions pour que le bouton reflète toujours
// exactement ce qu'il promet, quels que soient les filtres déjà en place.
boutonCoursesImminentes.addEventListener("click", () => {
  filtreImminentActif = !filtreImminentActif;
  boutonCoursesImminentes.classList.toggle("actif", filtreImminentActif);
  if (filtreImminentActif) {
    selecteurDate.value = formaterDate(new Date());
    for (const case_ of document.querySelectorAll('#filtre-decision-accueil input[type="checkbox"]')) {
      case_.checked = case_.value !== "Ne pas jouer";
    }
  }
  chargerReunions(selecteurDate.value);
});

chargerRoiGlobal();
chargerParisEnCours();
chargerHippodromes();
chargerReunions(selecteurDate.value);

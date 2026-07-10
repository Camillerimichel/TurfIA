// Page Accueil (cf. L018 §5) — réunions du jour, paris proposés par la
// dernière analyse de chaque course, et ROI global. Périmètre volontairement
// réduit pour ce premier incrément : pas de widgets « tâches automatiques »/
// « santé du système » (aucune automatisation planifiée construite, cf.
// PROJECT_STATE.md).

initialiserEntete();

function formaterDate(date) {
  return date.toISOString().slice(0, 10);
}

async function chargerRoiGlobal() {
  const conteneur = document.getElementById("widget-roi-global");
  try {
    const lignes = await apiFetch("/statistiques/globale");
    if (lignes.length === 0) {
      conteneur.textContent = "Aucune statistique calculée pour l'instant.";
      return;
    }
    const derniere = [...lignes].sort((a, b) => new Date(b.date_calcul) - new Date(a.date_calcul))[0];
    conteneur.innerHTML = "";
    const roi = document.createElement("p");
    roi.textContent = `ROI : ${derniere.roi !== null ? derniere.roi.toFixed(2) + " %" : "n/a"}`;
    const taux = document.createElement("p");
    taux.textContent = `Taux de réussite : ${derniere.taux_reussite !== null ? derniere.taux_reussite.toFixed(2) + " %" : "n/a"}`;
    const courses = document.createElement("p");
    courses.textContent = `${derniere.nb_courses} course(s) analysée(s), ${derniere.nb_jouees} jouée(s)`;
    const miseAJour = document.createElement("p");
    miseAJour.className = "note";
    miseAJour.textContent = `Dernière mise à jour : ${derniere.date_calcul ? formaterDateHeure(derniere.date_calcul) : "n/a"}`;
    conteneur.append(roi, taux, courses, miseAJour);
  } catch (erreur) {
    conteneur.textContent = `Erreur : ${erreur.message}`;
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

// "Jouer" exclut les décisions "Ne pas jouer" ainsi que les courses pas
// encore analysées (aucune décision) — seule "Toutes" les affiche.
function decisionCorrespondAuFiltre(decision, filtre) {
  if (filtre === "toutes") return true;
  if (filtre === "ne_pas_jouer") return decision === "Ne pas jouer";
  return decision != null && decision !== "Ne pas jouer";
}

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
    item.textContent = `${pari.type_pari} — combinaison ${pari.combinaison} — mise ${formaterMontant(pari.mise)} €`;
    liste.appendChild(item);
  }
  bloc.appendChild(liste);
  return bloc;
}

async function chargerReunions(dateJour) {
  const conteneur = document.getElementById("liste-reunions");
  conteneur.textContent = "Chargement…";
  const hippodromeId = document.getElementById("filtre-hippodrome-accueil").value;
  const filtreDecision = document.getElementById("filtre-decision-accueil").value;
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
          let decision = null;
          let contenuCourse;
          try {
            const detail = await chargerDerniereAnalyse(course.id);
            decision = detail ? detail.analyse.decision : null;
            if (!decisionCorrespondAuFiltre(decision, filtreDecision)) continue;
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
selecteurDate.value = formaterDate(new Date());
selecteurDate.addEventListener("change", () => chargerReunions(selecteurDate.value));
document.getElementById("filtre-hippodrome-accueil").addEventListener("change", () => chargerReunions(selecteurDate.value));
document.getElementById("filtre-decision-accueil").addEventListener("change", () => chargerReunions(selecteurDate.value));

chargerRoiGlobal();
chargerHippodromes();
chargerReunions(selecteurDate.value);

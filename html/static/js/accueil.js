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
    conteneur.append(roi, taux, courses);
  } catch (erreur) {
    conteneur.textContent = `Erreur : ${erreur.message}`;
  }
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
    `score ${detail.analyse.score_confiance ?? "n/a"} — budget ${detail.analyse.budget} €`;
  bloc.appendChild(entete);

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
    item.textContent = `${pari.type_pari} — combinaison ${pari.combinaison} — mise ${pari.mise} €`;
    liste.appendChild(item);
  }
  bloc.appendChild(liste);
  return bloc;
}

async function chargerReunions(dateJour) {
  const conteneur = document.getElementById("liste-reunions");
  conteneur.textContent = "Chargement…";
  try {
    const reunions = await apiFetch(`/reunions?date=${dateJour}`);
    if (reunions.length === 0) {
      conteneur.textContent = "Aucune réunion à cette date.";
      return;
    }
    conteneur.innerHTML = "";
    for (const reunion of reunions) {
      const bloc = document.createElement("div");
      bloc.className = "bloc-reunion";
      const titre = document.createElement("h3");
      titre.textContent = `R${reunion.numero} — hippodrome #${reunion.hippodrome_id} (${reunion.statut})`;
      bloc.appendChild(titre);

      try {
        const courses = await apiFetch(`/reunions/${reunion.id}/courses`);
        for (const course of courses) {
          const blocCourse = document.createElement("div");
          blocCourse.className = "bloc-course";

          const titreCourse = document.createElement("h4");
          const lien = document.createElement("a");
          lien.href = `/course.html?id=${course.id}`;
          lien.textContent = `C${course.numero} — ${course.nom}`;
          titreCourse.appendChild(lien);
          blocCourse.appendChild(titreCourse);

          try {
            const detail = await chargerDerniereAnalyse(course.id);
            if (detail === null) {
              const nonAnalysee = document.createElement("p");
              nonAnalysee.className = "note";
              nonAnalysee.textContent = "Pas encore analysée — cliquer sur la course pour lancer l'analyse.";
              blocCourse.appendChild(nonAnalysee);
            } else {
              blocCourse.appendChild(construireBlocParis(detail));
            }
          } catch (erreur) {
            const erreurParis = document.createElement("p");
            erreurParis.textContent = `Erreur paris : ${erreur.message}`;
            blocCourse.appendChild(erreurParis);
          }

          bloc.appendChild(blocCourse);
        }
      } catch (erreur) {
        const erreurCourses = document.createElement("p");
        erreurCourses.textContent = `Erreur : ${erreur.message}`;
        bloc.appendChild(erreurCourses);
      }
      conteneur.appendChild(bloc);
    }
  } catch (erreur) {
    conteneur.textContent = `Erreur : ${erreur.message}`;
  }
}

const selecteurDate = document.getElementById("selecteur-date");
selecteurDate.value = formaterDate(new Date());
selecteurDate.addEventListener("change", () => chargerReunions(selecteurDate.value));

chargerRoiGlobal();
chargerReunions(selecteurDate.value);

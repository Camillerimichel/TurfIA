// Client API partagé par toutes les pages — cf. L018 §3.3 (le JS ne fait que
// des appels API/interactions/rendu, aucune logique métier n'est dupliquée
// ici). Jeton opaque stocké en localStorage, envoyé en Authorization: Bearer
// (pas de cookies -> pas de protection CSRF nécessaire, cf. L018 §15).

const API_PREFIX = "/api/v1";
const CLE_JETON = "turfia_jeton";
const CLE_UTILISATEUR = "turfia_utilisateur";

function obtenirJeton() {
  return localStorage.getItem(CLE_JETON);
}

function definirSession(jeton, utilisateur) {
  localStorage.setItem(CLE_JETON, jeton);
  localStorage.setItem(CLE_UTILISATEUR, JSON.stringify(utilisateur));
}

function effacerSession() {
  localStorage.removeItem(CLE_JETON);
  localStorage.removeItem(CLE_UTILISATEUR);
}

function utilisateurCourant() {
  const brut = localStorage.getItem(CLE_UTILISATEUR);
  return brut ? JSON.parse(brut) : null;
}

// Redirige vers la connexion si aucun jeton n'est présent — à appeler en tête
// de chaque page protégée (toutes sauf login.html).
function exigerConnexion() {
  if (!obtenirJeton()) {
    window.location.href = "/login.html";
  }
}

async function apiFetch(chemin, options = {}) {
  const jeton = obtenirJeton();
  const entetes = { "Content-Type": "application/json", ...(options.headers || {}) };
  if (jeton) {
    entetes["Authorization"] = `Bearer ${jeton}`;
  }

  const reponse = await fetch(`${API_PREFIX}${chemin}`, { ...options, headers: entetes });

  if (reponse.status === 401) {
    effacerSession();
    window.location.href = "/login.html";
    throw new Error("Session expirée, reconnexion nécessaire.");
  }

  const corps = await reponse.json();
  if (!corps.success) {
    throw new Error(corps.error?.message || `Erreur ${reponse.status}`);
  }
  return corps.data;
}

// Bootstrap commun des pages protégées : exige une session, affiche
// l'utilisateur courant et branche le bouton de déconnexion (cf. entête
// partagée dupliquée dans index.html/course.html/statistiques.html — pas de
// moteur de gabarits, cf. L018 §3.1, mais ce petit bootstrap JS est partagé).
function initialiserEntete() {
  exigerConnexion();
  const utilisateur = utilisateurCourant();
  const span = document.getElementById("nom-utilisateur");
  if (span && utilisateur) {
    span.textContent = `${utilisateur.login} (${utilisateur.role})`;
  }
  const boutonDeconnexion = document.getElementById("bouton-deconnexion");
  if (boutonDeconnexion) {
    boutonDeconnexion.addEventListener("click", deconnecter);
  }
}

async function deconnecter() {
  try {
    await apiFetch("/auth/logout", { method: "POST" });
  } catch (erreur) {
    // Déconnexion locale même si l'appel serveur échoue (session déjà expirée, etc.)
  }
  effacerSession();
  window.location.href = "/login.html";
}

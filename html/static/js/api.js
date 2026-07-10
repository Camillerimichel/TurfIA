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

// Jauge « temps avant le départ » (cf. L018 §5-6) : verte quand il reste du
// temps, rouge sous 30 minutes — utilisée par l'Accueil et la fiche course
// pour toute course pas encore partie. Interpolation continue de teinte
// (120 = vert, 0 = rouge) plutôt que 2-3 couleurs fixes, pour un effet de
// jauge progressive.
const JAUGE_DEPART_SEUIL_ROUGE_MIN = 30;
const JAUGE_DEPART_SEUIL_VERT_MIN = 90;

function couleurJaugeDepart(minutesRestantes) {
  const ratio = Math.min(
    1,
    Math.max(
      0,
      (minutesRestantes - JAUGE_DEPART_SEUIL_ROUGE_MIN) / (JAUGE_DEPART_SEUIL_VERT_MIN - JAUGE_DEPART_SEUIL_ROUGE_MIN)
    )
  );
  return `hsl(${ratio * 120}, 70%, 40%)`;
}

function texteDureeAvantDepart(minutesRestantes) {
  const minutes = Math.round(minutesRestantes);
  if (minutes < 60) return `dans ${minutes} min`;
  const heures = Math.floor(minutes / 60);
  const reste = minutes % 60;
  return `dans ${heures} h ${String(reste).padStart(2, "0")}`;
}

function _rafraichirBadgeDepart(badge) {
  const heureDepart = new Date(badge.dataset.heureDepart);
  const minutesRestantes = (heureDepart - new Date()) / 60000;
  if (minutesRestantes <= 0) {
    badge.textContent = `${formaterDateHeure(badge.dataset.heureDepart)} (départ passé)`;
    badge.style.backgroundColor = "#8a8f98";
    return;
  }
  badge.textContent = `${formaterDateHeure(badge.dataset.heureDepart)} (${texteDureeAvantDepart(minutesRestantes)})`;
  badge.style.backgroundColor = couleurJaugeDepart(minutesRestantes);
}

// Construit le badge ; `heureDepartIso` est l'heure de départ (ISO, avec heure).
function construireBadgeDepart(heureDepartIso) {
  const badge = document.createElement("span");
  badge.className = "jauge-depart";
  badge.dataset.heureDepart = heureDepartIso;
  _rafraichirBadgeDepart(badge);
  return badge;
}

// Un seul intervalle global (30s suffit, pas besoin d'une précision à la
// seconde comme le compte à rebours Cron) : ne fait rien si aucun badge
// n'est présent sur la page courante.
setInterval(() => {
  for (const badge of document.querySelectorAll(".jauge-depart")) {
    _rafraichirBadgeDepart(badge);
  }
}, 30000);

// Indicateur de chargement global — un seul point de câblage pour toutes les
// pages (plutôt que de dupliquer un état de chargement par bouton/formulaire).
// Compteur de requêtes en vol : reste visible tant qu'au moins un appel est
// en cours, retiré uniquement quand le dernier se termine (succès ou échec).
// Durée minimale d'affichage : en local, une requête peut se terminer en
// quelques millisecondes — sans ce minimum, l'affichage puis le retrait
// peuvent arriver dans le même cycle de rendu et ne jamais être peints du
// tout (pas seulement « trop rapide pour être vu », littéralement invisible).
let _nbRequetesEnCours = 0;
let _instantAffichageIndicateur = null;
const DUREE_MINIMALE_AFFICHAGE_MS = 300;

function _obtenirIndicateurChargement() {
  let indicateur = document.getElementById("indicateur-chargement-global");
  if (!indicateur) {
    indicateur = document.createElement("div");
    indicateur.id = "indicateur-chargement-global";
    indicateur.textContent = "Chargement…";
    indicateur.hidden = true;
    document.body.prepend(indicateur);
  }
  return indicateur;
}

function _signalerDebutRequete() {
  _nbRequetesEnCours += 1;
  if (_nbRequetesEnCours === 1) {
    _instantAffichageIndicateur = Date.now();
    _obtenirIndicateurChargement().hidden = false;
  }
}

function _signalerFinRequete() {
  _nbRequetesEnCours = Math.max(0, _nbRequetesEnCours - 1);
  if (_nbRequetesEnCours > 0) return;

  const attente = Math.max(0, DUREE_MINIMALE_AFFICHAGE_MS - (Date.now() - _instantAffichageIndicateur));
  setTimeout(() => {
    if (_nbRequetesEnCours === 0) {
      _obtenirIndicateurChargement().hidden = true;
    }
  }, attente);
}

// Formatage horaire commun à toutes les pages (cf. L018 §12) : toute valeur
// ISO datetime (avec heure) affichée dans l'interface doit l'être au format
// JJ/MM/AAAA - HH:MM. Les dates seules (sans heure, ex. jour de réunion) ne
// sont pas concernées — `MOTIF_DATE_ISO` exige un composant heure.
const MOTIF_DATE_ISO = /^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}/;

function formaterDateHeure(valeurIso) {
  const date = new Date(valeurIso);
  if (Number.isNaN(date.getTime())) return valeurIso;
  const deuxChiffres = (n) => String(n).padStart(2, "0");
  return (
    `${deuxChiffres(date.getDate())}/${deuxChiffres(date.getMonth() + 1)}/${date.getFullYear()}` +
    ` - ${deuxChiffres(date.getHours())}:${deuxChiffres(date.getMinutes())}`
  );
}

// Formatage monétaire commun (cf. L018 §12) : tout montant en euros affiché
// dans l'interface a un séparateur de milliers " ". Le séparateur décimal
// reste "." (non concerné par la demande), toujours 2 décimales.
function formaterMontant(valeur) {
  const nombre = Number(valeur);
  if (valeur === null || valeur === undefined || Number.isNaN(nombre)) return "n/a";
  const negatif = nombre < 0;
  const [entier, decimal] = Math.abs(nombre).toFixed(2).split(".");
  const entierGroupe = entier.replace(/\B(?=(\d{3})+(?!\d))/g, " ");
  return `${negatif ? "-" : ""}${entierGroupe}.${decimal}`;
}

async function apiFetch(chemin, options = {}) {
  const jeton = obtenirJeton();
  const entetes = { "Content-Type": "application/json", ...(options.headers || {}) };
  if (jeton) {
    entetes["Authorization"] = `Bearer ${jeton}`;
  }

  _signalerDebutRequete();
  try {
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
  } finally {
    _signalerFinRequete();
  }
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

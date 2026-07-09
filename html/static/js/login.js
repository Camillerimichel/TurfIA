// Page de connexion — cf. api.js pour le client API partagé.

document.getElementById("formulaire-connexion").addEventListener("submit", async (evenement) => {
  evenement.preventDefault();
  const login = document.getElementById("login").value;
  const motDePasse = document.getElementById("mot-de-passe").value;
  const messageErreur = document.getElementById("message-erreur");
  messageErreur.hidden = true;

  try {
    const data = await apiFetch("/auth/login", {
      method: "POST",
      body: JSON.stringify({ login, mot_de_passe: motDePasse }),
    });
    definirSession(data.jeton, data.utilisateur);
    window.location.href = "/";
  } catch (erreur) {
    messageErreur.textContent = erreur.message;
    messageErreur.hidden = false;
  }
});

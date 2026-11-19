"""
Étape 5 : Génération d'explications en langage naturel via Ollama (Mistral)
pour chaque recommandation produite par KMeans + KNN.
Support multilingue : change LANGUE_CHOISIE selon l'agent qui va lire.
"""

import pandas as pd
import ollama

recommandations = pd.read_csv("recommandations.csv", encoding="utf-8-sig")
clients = pd.read_csv("clients_avec_segments.csv", encoding="utf-8-sig")

NOMS_PRODUITS = {
    "deposit": "Compte de Dépôt",
    "saving": "Compte d'Épargne",
    "linkedsaving": "Épargne Liée",
}

LANGUES = {
    "fr": "français",
    "en": "anglais",
    "ar": "arabe",
}

# ---- Change ici selon l'agent qui va lire les explications ----
LANGUE_CHOISIE = "fr"  # "fr", "en" ou "ar"


def message_systeme(langue):
    nom_langue = LANGUES[langue]
    return (f"Tu es un assistant qui aide les agents d'une banque tunisienne à comprendre "
            f"des recommandations produit. Tu réponds TOUJOURS en {nom_langue}, jamais dans "
            f"une autre langue, quelle que soit la question.")


def construire_prompt(client_row, produit, score, langue):
    if score >= 0.8:
        niveau_confiance = "élevé"
    elif score >= 0.6:
        niveau_confiance = "modéré"
    else:
        niveau_confiance = "faible"

    nom_langue = LANGUES[langue]
    return f"""Voici le profil du client :
- Segment : {client_row['segment']}
- Âge : {client_row['age']} ans
- Statut civil : {client_row['civilstatus_']}
- Nombre de comptes actuels : {client_row['nombre_comptes_total']}
- Produits déjà détenus : {client_row['nb_deposit']} Dépôt, {client_row['nb_saving']} Épargne, {client_row['nb_linkedsaving']} Épargne Liée

Recommandation générée par l'algorithme : proposer le produit "{NOMS_PRODUITS[produit]}"
Score de confiance : {score} — niveau {niveau_confiance}

Rédige une explication courte (2-3 phrases maximum), en {nom_langue} uniquement, en une phrase fluide et professionnelle (pas une liste de données), que l'agent peut lire avant d'appeler le client. Reste calibré au niveau de confiance indiqué : ne dis pas "fortement recommandé" si le niveau est modéré. N'invente aucune information qui n'est pas donnée ci-dessus."""


explications = []

# on limite à 5 pour un premier test rapide (Mistral en CPU est lent)
for _, reco in recommandations.head(5).iterrows():
    client_row = clients[clients["client_id"] == reco["client_id"]].iloc[0]
    prompt = construire_prompt(client_row, reco["produit_recommande"], reco["score_confiance"], LANGUE_CHOISIE)

    reponse = ollama.chat(
        model="mistral:7b-instruct-q4_0",
        messages=[
            {"role": "system", "content": message_systeme(LANGUE_CHOISIE)},
            {"role": "user", "content": prompt},
        ],
        options={"temperature": 0.3},
    )

    texte = reponse["message"]["content"]
    explications.append({
        "client_id": reco["client_id"],
        "produit_recommande": reco["produit_recommande"],
        "score_confiance": reco["score_confiance"],
        "langue": LANGUE_CHOISIE,
        "explication": texte,
    })
    print(f"Client {reco['client_id']} : {texte}\n{'-'*60}")

pd.DataFrame(explications).to_csv("explications.csv", index=False, encoding="utf-8-sig")
print("\nSauvegardé : explications.csv")
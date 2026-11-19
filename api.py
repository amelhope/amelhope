from fastapi import FastAPI, HTTPException
import pandas as pd

app = FastAPI(title="API Moteur de Recommandation LANALA")

clients = pd.read_csv("clients_avec_segments.csv", encoding="utf-8-sig")
recommandations = pd.read_csv("recommandations.csv", encoding="utf-8-sig")

NOMS_PRODUITS = {
    "deposit": "Compte de Dépôt",
    "saving": "Compte d'Épargne",
    "linkedsaving": "Épargne Liée",
}


@app.get("/")
def accueil():
    return {"message": "Mon API fonctionne !"}


@app.get("/recommandation/{client_id}")
def get_recommandation(client_id: int):
    client = clients[clients["client_id"] == client_id]
    if client.empty:
        raise HTTPException(status_code=404, detail=f"Client {client_id} introuvable")

    client_row = client.iloc[0]
    reco = recommandations[recommandations["client_id"] == client_id]

    if reco.empty:
        return {
            "client_id": client_id,
            "segment": client_row["segment"],
            "recommandation": None,
            "message": "Ce client possède déjà les 3 produits disponibles — aucune recommandation possible.",
        }

    produit = reco.iloc[0]["produit_recommande"]
    score = float(reco.iloc[0]["score_confiance"])
    nom_produit = NOMS_PRODUITS.get(produit, produit)

    pourcentage = round(score * 100)
    explication = (
        f"Ce client appartient au segment {client_row['segment']}. "
        f"Parmi ses clients les plus similaires, {pourcentage}% possèdent déjà "
        f"le produit {nom_produit}."
    )

    return {
        "client_id": client_id,
        "segment": client_row["segment"],
        "recommandation": produit,
        "recommandation_libelle": nom_produit,
        "score_confiance": score,
        "explication": explication,
    }
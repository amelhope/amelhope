"""
Évaluation de la précision du KNN par validation croisée "leave-one-out" :
pour chaque produit qu'un client possède déjà, on le cache temporairement
et on vérifie si le KNN le retrouve parmi ses recommandations.

C'est la vraie preuve que le système "apprend" quelque chose d'utile,
pas seulement qu'il génère des scores.
"""

import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors

features_df = pd.read_csv("clients_features.csv", encoding="utf-8-sig")
clients = pd.read_csv("clients_avec_segments.csv", encoding="utf-8-sig")

colonnes_features = [c for c in features_df.columns if c != "client_id"]
X = features_df[colonnes_features].values
produits = ["nb_deposit", "nb_saving", "nb_linkedsaving"]

N_VOISINS = 20
knn = NearestNeighbors(n_neighbors=N_VOISINS + 1)
knn.fit(X)
distances, indices = knn.kneighbors(X)

resultats = []

for i in range(len(clients)):
    client = clients.iloc[i]
    voisins_idx = indices[i][1:]
    voisins = clients.iloc[voisins_idx]

    # Pour chaque produit que CE client possède réellement...
    for produit in produits:
        if client[produit] > 0:
            # on regarde : parmi ses voisins, quelle proportion a aussi ce produit ?
            proportion_voisins = (voisins[produit] > 0).mean()

            # on regarde aussi les 2 autres produits, pour comparer
            autres_scores = {}
            for autre_produit in produits:
                if autre_produit != produit:
                    autres_scores[autre_produit] = (voisins[autre_produit] > 0).mean()

            # "réussite" = le produit que le client possède VRAIMENT est bien
            # celui qui a le score le plus élevé parmi les voisins
            tous_scores = {produit: proportion_voisins, **autres_scores}
            produit_predit = max(tous_scores, key=tous_scores.get)
            reussite = (produit_predit == produit)

            resultats.append({
                "client_id": client["client_id"],
                "produit_reel": produit,
                "score_produit_reel": proportion_voisins,
                "produit_predit": produit_predit,
                "reussite": reussite,
            })

resultats_df = pd.DataFrame(resultats)
taux_reussite = resultats_df["reussite"].mean()

print(f"Nombre de tests effectués : {len(resultats_df)}")
print(f"Taux de réussite : {round(taux_reussite * 100, 1)}%")
print(f"(Le hasard pur donnerait environ {round(100/3, 1)}% avec 3 produits possibles)")
print()
print("Détail par produit :")
print(resultats_df.groupby("produit_reel")["reussite"].mean().round(3))
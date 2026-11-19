"""
Version étendue : teste des valeurs de K plus grandes pour voir si le
score de confiance continue de s'améliorer au-delà de K=20.
"""

import pandas as pd
from sklearn.neighbors import NearestNeighbors

features_df = pd.read_csv("clients_features.csv", encoding="utf-8-sig")
clients = pd.read_csv("clients_avec_segments.csv", encoding="utf-8-sig")

colonnes_features = [c for c in features_df.columns if c != "client_id"]
X = features_df[colonnes_features]
produits = ["nb_deposit", "nb_saving", "nb_linkedsaving"]

def tester_k(n_voisins):
    knn = NearestNeighbors(n_neighbors=n_voisins + 1)
    knn.fit(X)
    distances, indices = knn.kneighbors(X)

    scores = []
    for i in range(len(features_df)):
        voisins_idx = indices[i][1:]
        voisins = clients.iloc[voisins_idx]
        client_actuel = clients.iloc[i]

        meilleur_score = -1
        a_un_produit_manquant = False
        for produit in produits:
            if client_actuel[produit] == 0:
                a_un_produit_manquant = True
                proportion = (voisins[produit] > 0).mean()
                meilleur_score = max(meilleur_score, proportion)

        if a_un_produit_manquant:
            scores.append(meilleur_score)

    return {
        "K": n_voisins,
        "nb_recommandations": len(scores),
        "score_moyen": round(sum(scores) / len(scores), 3) if scores else 0,
    }

resultats = [tester_k(k) for k in [20, 30, 50, 80, 120]]
resultats_df = pd.DataFrame(resultats)
print(resultats_df.to_string(index=False))
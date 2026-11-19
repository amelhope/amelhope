"""
Évaluation du KNN avec une vraie séparation train/test (80/20).
"""

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.neighbors import NearestNeighbors

features_df = pd.read_csv("clients_features.csv", encoding="utf-8-sig")
clients = pd.read_csv("clients_avec_segments.csv", encoding="utf-8-sig")

produits = ["nb_deposit", "nb_saving", "nb_linkedsaving"]
colonnes_features = [c for c in features_df.columns if c not in ("client_id", "split")]

# --- Séparation train (80%) / test (20%) ---
train_idx, test_idx = train_test_split(
    features_df.index, test_size=0.2, random_state=42
)

X_train = features_df.loc[train_idx, colonnes_features]
X_test = features_df.loc[test_idx, colonnes_features]

clients_train = clients.loc[train_idx].reset_index(drop=True)
clients_test = clients.loc[test_idx].reset_index(drop=True)

print(f"Train : {len(X_train)} clients (servent de voisins)")
print(f"Test  : {len(X_test)} clients (jamais vus, servent uniquement à évaluer)")
print()


def tester_precision_train_test(n_voisins):
    knn = NearestNeighbors(n_neighbors=n_voisins)
    knn.fit(X_train)

    distances, indices = knn.kneighbors(X_test)

    reussites = []
    for i in range(len(clients_test)):
        client = clients_test.iloc[i]
        voisins = clients_train.iloc[indices[i]]

        for produit in produits:
            if client[produit] > 0:
                scores_produits = {
                    p: (voisins[p] > 0).mean() for p in produits
                }
                produit_predit = max(scores_produits, key=scores_produits.get)
                reussites.append(produit_predit == produit)

    return {
        "K": n_voisins,
        "nb_tests": len(reussites),
        "taux_reussite": round(sum(reussites) / len(reussites) * 100, 1) if reussites else 0,
    }


resultats = [tester_precision_train_test(k) for k in [10, 20, 30, 50]]
resultats_df = pd.DataFrame(resultats)
print(resultats_df.to_string(index=False))
print()
print("Rappel : le hasard pur donnerait environ 33.3%")
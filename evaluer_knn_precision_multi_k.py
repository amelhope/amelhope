"""
Évaluation rigoureuse : 
- KNN entraîné sur TRAIN uniquement (2400 clients)
- Précision évaluée sur TEST uniquement (600 clients)
- Compare plusieurs K (20, 30, 50, 80, 120)
- Mesure : parmi les produits que les clients TEST possèdent,
  combien sont correctement prédits comme "le meilleur" ?
"""

import pandas as pd
from sklearn.neighbors import NearestNeighbors

features_df = pd.read_csv("clients_features.csv", encoding="utf-8-sig")
clients = pd.read_csv("clients_avec_segments.csv", encoding="utf-8-sig")

colonnes_features = [c for c in features_df.columns if c not in ["client_id", "split"]]
X_all = features_df[colonnes_features].values

train_mask = features_df["split"] == "train"
test_mask = features_df["split"] == "test"

X_train = features_df.loc[train_mask, colonnes_features].values
X_test = features_df.loc[test_mask, colonnes_features].values

train_indices = features_df.index[train_mask].tolist()
test_indices = features_df.index[test_mask].tolist()

print(f"Évaluation KNN sur données de TEST (séparation train/test)")
print(f"  TRAIN : {len(X_train)} clients")
print(f"  TEST  : {len(X_test)} clients\n")

produits = ["nb_deposit", "nb_saving", "nb_linkedsaving"]


def tester_precision(n_voisins):
    """
    Entraîne KNN sur TRAIN, évalue la précision sur TEST.
    Mesure : pour chaque produit que le client TEST possède,
    est-ce que c'est le produit le mieux recommandé ?
    """
    knn = NearestNeighbors(n_neighbors=n_voisins)
    knn.fit(X_train)
    
    distances, indices = knn.kneighbors(X_test)

    reussites = []
    
    for i, test_idx in enumerate(test_indices):
        client = clients.iloc[test_idx]
        voisins_train_indices = indices[i]
        
        voisins_indices_original = [train_indices[vi] for vi in voisins_train_indices]
        voisins = clients.iloc[voisins_indices_original]

        for produit in produits:
            if client[produit] > 0:
                scores_produits = {}
                for p in produits:
                    scores_produits[p] = (voisins[p] > 0).mean()
                
                produit_predit = max(scores_produits, key=scores_produits.get)
                
                reussites.append(produit_predit == produit)

    if len(reussites) == 0:
        return None
    
    taux = sum(reussites) / len(reussites) * 100
    return {
        "K": n_voisins,
        "nb_tests": len(reussites),
        "taux_reussite": round(taux, 1),
    }


print("Comparaison de précision pour différentes valeurs de K :\n")
resultats = [tester_precision(k) for k in [20, 30, 50, 80, 120]]
resultats = [r for r in resultats if r is not None]

resultats_df = pd.DataFrame(resultats)
print(resultats_df.to_string(index=False))
print()
print("\n✅ Baseline : un système de recommandation fiable dépasse ~45-50%")
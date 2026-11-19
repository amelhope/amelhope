"""
Compare K=3 vs K=5 sur des stats métier (âge, revenu, nb comptes moyens
par cluster), pour choisir le K le plus interprétable.
"""

import pandas as pd
from sklearn.cluster import KMeans

features_df = pd.read_csv("clients_features.csv", encoding="utf-8-sig")
clients_aggreges = pd.read_csv("clients_aggreges.csv", encoding="utf-8-sig")
colonnes_features = [c for c in features_df.columns if c not in ("client_id", "split")]
X = features_df[colonnes_features]

for k in [3, 5]:
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    clusters = km.fit_predict(X)

    temp = clients_aggreges.copy()
    temp["cluster"] = clusters

    print(f"\n{'='*50}\nK = {k}\n{'='*50}")
    resume = temp.groupby("cluster").agg(
        nb_clients=("client_id", "count"),
        age_moyen=("age", "mean"),
        revenu_moyen=("revenu_mensuel", "mean"),
        nb_comptes_moyen=("nombre_comptes_total", "mean"),
    ).round(1)
    print(resume)
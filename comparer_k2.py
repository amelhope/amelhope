import pandas as pd
from sklearn.cluster import KMeans

features_df = pd.read_csv("clients_features.csv", encoding="utf-8-sig")
clients_aggreges = pd.read_csv("clients_aggreges.csv", encoding="utf-8-sig")
colonnes_features = [c for c in features_df.columns if c != "client_id"]
X = features_df[colonnes_features]

km = KMeans(n_clusters=2, random_state=42, n_init=10)
clients_aggreges["cluster"] = km.fit_predict(X)

print(clients_aggreges.groupby("cluster").agg(
    nb_clients=("client_id", "count"),
    age_moyen=("age", "mean"),
    revenu_moyen=("revenu_mensuel", "mean"),
    nb_comptes_moyen=("nombre_comptes_total", "mean"),
).round(1))
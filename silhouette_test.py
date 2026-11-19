import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

features_df = pd.read_csv("clients_features.csv", encoding="utf-8-sig")
colonnes_features = [c for c in features_df.columns if c != "client_id"]
X = features_df[colonnes_features]

print("K | Score de silhouette (plus proche de 1 = meilleur)")
for k in range(2, 9):
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    clusters = km.fit_predict(X)
    score = silhouette_score(X, clusters)
    print(f"K={k} : {round(score, 3)}")
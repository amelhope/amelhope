"""
K-Means entraîné sur TRAIN uniquement, prédiction sur TOUS (train + test).
Évite le data leakage sur la segmentation.
"""
import pandas as pd
from sklearn.cluster import KMeans

features_df = pd.read_csv("clients_features.csv", encoding="utf-8-sig")
clients_aggreges = pd.read_csv("clients_aggreges.csv", encoding="utf-8-sig")

clients_aggreges["split"] = features_df["split"]

colonnes_features = [c for c in features_df.columns if c not in ["client_id", "split"]]

train_mask = features_df["split"] == "train"
X_train = features_df.loc[train_mask, colonnes_features]

print(f"Entraînement K-Means sur {sum(train_mask)} clients (TRAIN)")

kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
kmeans.fit(X_train)

X_all = features_df[colonnes_features]
clients_aggreges["cluster"] = kmeans.predict(X_all)

# Les noms de segments (Modeste/Intermediaire/Premium) sont définis à partir
# du revenu moyen par cluster, calculé sur TRAIN uniquement (pas de leakage).
train_clients_temp = clients_aggreges[clients_aggreges["split"] == "train"]
revenu_moyen_par_cluster = train_clients_temp.groupby("cluster")["revenu_mensuel"].mean().sort_values()
noms = {revenu_moyen_par_cluster.index[0]: "Modeste",
        revenu_moyen_par_cluster.index[1]: "Intermediaire",
        revenu_moyen_par_cluster.index[2]: "Premium"}
clients_aggreges["segment"] = clients_aggreges["cluster"].map(noms)

clients_aggreges.to_csv("clients_avec_segments.csv", index=False, encoding="utf-8-sig")

# IMPORTANT : on recalcule train_clients / test_clients ICI, une fois que
# la colonne "segment" existe bien dans clients_aggreges.
train_clients = clients_aggreges[clients_aggreges["split"] == "train"]
test_clients = clients_aggreges[clients_aggreges["split"] == "test"]

print(f"\nDistribution des segments (TOUS les clients) :")
print(clients_aggreges["segment"].value_counts())
print(f"\nDistribution des segments (TRAIN uniquement) :")
print(train_clients["segment"].value_counts())
print(f"\nDistribution des segments (TEST uniquement) :")
print(test_clients["segment"].value_counts())

print("\nSauvegardé : clients_avec_segments.csv (avec colonne split)")
"""
Évaluation de la stabilité du KMeans : on relance le clustering plusieurs
fois avec des points de départ différents, et on mesure à quel point les
groupes obtenus se ressemblent (Adjusted Rand Index, 1.0 = identique).
"""

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score

features_df = pd.read_csv("clients_features.csv", encoding="utf-8-sig")
colonnes_features = [c for c in features_df.columns if c not in ("client_id", "split")]
X = features_df[colonnes_features]

K = 3
SEEDS = [0, 1, 2, 3, 4, 10, 20, 42, 100, 123]

resultats_clustering = []
for seed in SEEDS:
    km = KMeans(n_clusters=K, random_state=seed, n_init=10)
    labels = km.fit_predict(X)
    resultats_clustering.append(labels)

scores_ari = []
for i in range(len(resultats_clustering)):
    for j in range(i + 1, len(resultats_clustering)):
        from sklearn.metrics import adjusted_rand_score
        ari = adjusted_rand_score(resultats_clustering[i], resultats_clustering[j])
        scores_ari.append(ari)

import numpy as np
print(f"Nombre de comparaisons effectuées : {len(scores_ari)}")
print(f"ARI moyen : {round(np.mean(scores_ari), 3)}")
print(f"ARI minimum : {round(np.min(scores_ari), 3)}")
print(f"ARI maximum : {round(np.max(scores_ari), 3)}")
print()
print("Interprétation :")
print("  ARI proche de 1.0 -> clustering très stable")
print("  ARI proche de 0.0 -> clustering instable")
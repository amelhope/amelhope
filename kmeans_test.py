"""
Étape 3 : Méthode du coude + entraînement KMeans + comparaison avec les personas
"""

import pandas as pd
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

features_df = pd.read_csv("clients_features.csv", encoding="utf-8-sig")
colonnes_features = [c for c in features_df.columns if c != "client_id"]
X = features_df[colonnes_features]

# ---- 1. Méthode du coude : tester plusieurs K et regarder l'inertie ----
inerties = []
valeurs_k = range(1, 11)
for k in valeurs_k:
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    km.fit(X)
    inerties.append(km.inertia_)

plt.figure(figsize=(8, 5))
plt.plot(valeurs_k, inerties, marker="o")
plt.xlabel("Nombre de clusters (K)")
plt.ylabel("Inertie")
plt.title("Méthode du coude")
plt.savefig("methode_du_coude.png")
print("Graphique sauvegardé : methode_du_coude.png")
print("\nInerties par K:")
for k, inertie in zip(valeurs_k, inerties):
    print(f"K={k}: {round(inertie, 1)}")

# ---- 2. Entraîner le KMeans avec K=5 (nombre de personas connus) ----
kmeans_final = KMeans(n_clusters=5, random_state=42, n_init=10)
clusters = kmeans_final.fit_predict(X)

features_df["cluster"] = clusters

# ---- 3. Comparer avec les vrais personas (pour validation uniquement) ----
clients_aggreges = pd.read_csv("clients_aggreges.csv", encoding="utf-8-sig")
comparaison = features_df[["client_id", "cluster"]].merge(
    clients_aggreges[["client_id"]], on="client_id"
)

# on récupère persona depuis le fichier détaillé (clients_synthetiques.csv)
originaux = pd.read_csv("clients_synthetiques.csv", encoding="utf-8-sig")
persona_par_client = originaux.groupby("client_id")["persona"].first().reset_index()
comparaison = comparaison.merge(persona_par_client, on="client_id")

print("\n--- Répartition persona x cluster (tableau croisé) ---")
print(pd.crosstab(comparaison["persona"], comparaison["cluster"]))

comparaison.to_csv("resultat_clusters.csv", index=False, encoding="utf-8-sig")
print("\nRésultat détaillé sauvegardé : resultat_clusters.csv")
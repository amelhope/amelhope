"""
Étape 2 (corrigée) : Encodage + standardisation, prêt pour le KMeans
Gère tous les statuts civils (Married/Single/Divorced/Widowed) via one-hot encoding.

Corrections apportées :
1. Le split train/test est maintenant VRAIMENT aléatoire (le shuffle était
   calculé mais jamais utilisé dans la version précédente).
2. Le StandardScaler est fit UNIQUEMENT sur le train, puis appliqué
   (transform) à train + test — évite la fuite de données (data leakage).
"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

df = pd.read_csv("clients_aggreges.csv", encoding="utf-8-sig")

# ========== Split train/test (VRAIMENT aléatoire, avant tout traitement) ==========
np.random.seed(42)
n_clients = len(df)
n_train = int(n_clients * 0.8)

shuffled_positions = np.arange(n_clients)
np.random.shuffle(shuffled_positions)

split = np.array(["test"] * n_clients, dtype=object)
split[shuffled_positions[:n_train]] = "train"
df["split"] = split

print(f"\nSplit train/test créé (random_state=42, réellement aléatoire) :")
print(f"  TRAIN : {(split == 'train').sum()} clients (80%)")
print(f"  TEST  : {(split == 'test').sum()} clients (20%)")

civilstatus_dummies = pd.get_dummies(df["civilstatus_"], prefix="civilstatus").astype(int)
df = pd.concat([df, civilstatus_dummies], axis=1)

colonnes_produits = ["nombre_comptes_total", "nombre_types_produits_distincts",
                      "nb_deposit", "nb_linkedsaving", "nb_saving"]
colonnes_features = (
    ["age"]
    + list(civilstatus_dummies.columns)
    + ["nombre_enfants", "nombre_conjoints", "revenu_mensuel"]
    + colonnes_produits
)

features = df[colonnes_features].copy()

# ========== Standardisation : fit sur TRAIN uniquement (évite le leakage) ==========
train_mask = (df["split"] == "train").values

scaler = StandardScaler()
scaler.fit(features[train_mask])                      # apprend mean/std sur TRAIN seul
features_standardisees = scaler.transform(features)   # applique à TOUT (train + test)

features_df = pd.DataFrame(features_standardisees, columns=colonnes_features)
features_df.insert(0, "split", df["split"].values)
features_df.insert(0, "client_id", df["client_id"].values)
features_df.to_csv("clients_features.csv", index=False, encoding="utf-8-sig")

print(f"\n{len(features_df)} clients prêts pour le KMeans")
print(f"Statuts civils détectés et encodés : {list(civilstatus_dummies.columns)}")
print("\nVérification : aucune valeur manquante ?")
print(features_df.isna().sum().sum(), "valeur(s) manquante(s) au total (doit être 0)")
print("\nAperçu des features standardisées (avec split) :")
print(features_df.head())
"""
KNN v5 (production) :
- Entraîné sur TOUS les clients (3000).
- Pour chaque client, calcule la confidence (proportion de voisins
  possédant le produit) pour TOUS les produits manquants, pas
  seulement le meilleur.
- Baseline "éligible" par produit : moyenne de la confidence,
  calculée UNIQUEMENT sur les clients qui ne possèdent pas non plus
  ce produit (leave-one-out : chaque client est exclu de son propre
  baseline). Corrige le biais du lift "global" (comparer un client
  sans le produit à une population dominée par ceux qui l'ont).
- Le produit recommandé est choisi sur la base du LIFT ÉLIGIBLE
  (le plus haut), pas du score brut — évite de recommander
  automatiquement le seul produit manquant même s'il est en réalité
  peu pertinent pour ce client.
- lift_global est conservé en plus, à titre de comparaison.
"""

import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors

features_df = pd.read_csv("clients_features.csv", encoding="utf-8-sig")
clients = pd.read_csv("clients_avec_segments.csv", encoding="utf-8-sig")

colonnes_features = [c for c in features_df.columns if c not in ["client_id", "split"]]
X_all = features_df[colonnes_features].values
n_clients = len(X_all)

print(f"Entraînement KNN (production) sur {n_clients} clients (TOUS)")

N_VOISINS = 20
knn = NearestNeighbors(n_neighbors=N_VOISINS + 1)  # +1 pour exclure soi-même
knn.fit(X_all)
distances, indices = knn.kneighbors(X_all)

produits = ["nb_deposit", "nb_saving", "nb_linkedsaving"]

# ========== Étape 1 : matrice complète des scores (client x produit manquant) ==========
scores = {p: np.full(n_clients, np.nan) for p in produits}
manque = {p: np.zeros(n_clients, dtype=bool) for p in produits}

for i in range(n_clients):
    voisins_indices = [idx for idx in indices[i] if idx != i][:N_VOISINS]
    voisins = clients.iloc[voisins_indices]
    client_actuel = clients.iloc[i]
    for p in produits:
        if client_actuel[p] == 0:
            manque[p][i] = True
            scores[p][i] = (voisins[p] > 0).mean()

# ========== Étape 2 : baseline global (pour comparaison) et baseline éligible (leave-one-out) ==========
taux_global = {p: (clients[p] > 0).mean() for p in produits}

sommes_eligibles = {p: np.nansum(scores[p]) for p in produits}
n_eligibles = {p: manque[p].sum() for p in produits}

print("\nBaseline par produit :")
for p in produits:
    print(f"  {p:15s} : global = {taux_global[p] * 100:.1f}% | "
          f"éligible (moyenne des {n_eligibles[p]} clients sans ce produit) = "
          f"{(sommes_eligibles[p] / n_eligibles[p]) * 100:.1f}%")

# ========== Étape 3 : choisir le produit recommandé sur la base du lift ÉLIGIBLE ==========
def categoriser(lift):
    if np.isnan(lift):
        return None
    if lift < 0.8:
        return "Defavorable (<0.8)"
    elif lift <= 1.3:
        return "Neutre (0.8-1.3)"
    else:
        return "Favorable (>1.3)"


recommandations = []
clients_sans_produit_manquant = 0

for i in range(n_clients):
    client_actuel = clients.iloc[i]
    candidats = []

    for p in produits:
        if not manque[p][i]:
            continue

        score_i = scores[p][i]

        # baseline éligible en excluant le client lui-même (leave-one-out)
        n_elig = n_eligibles[p]
        if n_elig > 1:
            baseline_eligible = (sommes_eligibles[p] - score_i) / (n_elig - 1)
        else:
            baseline_eligible = np.nan

        lift_eligible = (score_i / baseline_eligible) if baseline_eligible and baseline_eligible > 0 else np.nan
        lift_global = (score_i / taux_global[p]) if taux_global[p] > 0 else np.nan

        candidats.append({
            "produit": p,
            "score": score_i,
            "baseline_eligible": baseline_eligible,
            "lift_eligible": lift_eligible,
            "lift_global": lift_global,
        })

    if not candidats:
        clients_sans_produit_manquant += 1
        continue

    # on choisit le produit avec le meilleur LIFT ÉLIGIBLE (pas le score brut)
    candidats_valides = [c for c in candidats if not np.isnan(c["lift_eligible"])]
    meilleur = max(candidats_valides, key=lambda c: c["lift_eligible"]) if candidats_valides else candidats[0]

    recommandations.append({
        "client_id": features_df.iloc[i]["client_id"],
        "segment": client_actuel["segment"],
        "produit_recommande": meilleur["produit"].replace("nb_", ""),
        "score_confiance": round(meilleur["score"], 3),
        "baseline_eligible": round(meilleur["baseline_eligible"], 3) if not np.isnan(meilleur["baseline_eligible"]) else None,
        "lift_eligible": round(meilleur["lift_eligible"], 2) if not np.isnan(meilleur["lift_eligible"]) else None,
        "lift_global": round(meilleur["lift_global"], 2) if not np.isnan(meilleur["lift_global"]) else None,
        "categorie_lift": categoriser(meilleur["lift_eligible"]),
    })

reco_df = pd.DataFrame(recommandations)
reco_df.to_csv("recommandations.csv", index=False, encoding="utf-8-sig")

print(f"\n{len(reco_df)} recommandations générées sur {n_clients} clients "
      f"({clients_sans_produit_manquant} clients possèdent déjà les 3 produits).")

print("\nRépartition par catégorie de lift éligible :")
print(reco_df["categorie_lift"].value_counts())

print("\nComparaison lift_eligible vs lift_global (statistiques) :")
print(reco_df[["lift_eligible", "lift_global"]].describe().round(2))

print("\nRépartition des produits recommandés :")
print(reco_df["produit_recommande"].value_counts())
"""
Analyse de la distribution du lift sur l'ensemble des recommandations
(recommandations.csv, généré par knn_recommandation.py v4 - production,
sur les 3000 clients).

Objectif : valider empiriquement si des seuils comme 0.8 / 1.3 sont
pertinents sur CE dataset, avant de les intégrer dans le système de
recommandation. Ne modifie rien, ne fait que mesurer.
"""

import pandas as pd

clients = pd.read_csv("clients_avec_segments.csv", encoding="utf-8-sig")
recommandations = pd.read_csv("recommandations.csv", encoding="utf-8-sig")

COLONNES_PRODUITS = {
    "deposit": "nb_deposit",
    "saving": "nb_saving",
    "linkedsaving": "nb_linkedsaving",
}

# Taux de possession global (population générale = les 3000 clients,
# cohérent avec knn_recommandation.py v4 qui est entraîné sur les 3000).
taux_global = {
    produit: (clients[col] > 0).mean()
    for produit, col in COLONNES_PRODUITS.items()
}

print("Taux de possession global par produit :")
for produit, taux in taux_global.items():
    print(f"  {produit:15s} : {taux * 100:.1f}%")

# ========== Calcul du lift pour chaque recommandation ==========
recommandations = recommandations.copy()
recommandations["support_global"] = recommandations["produit_recommande"].map(taux_global)
recommandations["lift"] = recommandations["score_confiance"] / recommandations["support_global"]


def categoriser(lift):
    if lift < 0.8:
        return "Defavorable (<0.8)"
    elif lift <= 1.3:
        return "Neutre (0.8-1.3)"
    else:
        return "Favorable (>1.3)"


recommandations["categorie_lift"] = recommandations["lift"].apply(categoriser)

# ========== Statistiques globales ==========
n = len(recommandations)
print(f"\n{'=' * 60}")
print(f"DISTRIBUTION GLOBALE DU LIFT ({n} recommandations)")
print(f"{'=' * 60}")

stats = recommandations["lift"].describe()
print(f"\nMinimum : {stats['min']:.2f}")
print(f"Q1      : {stats['25%']:.2f}")
print(f"Médiane : {stats['50%']:.2f}")
print(f"Q3      : {stats['75%']:.2f}")
print(f"Maximum : {stats['max']:.2f}")
print(f"Moyenne : {stats['mean']:.2f}")

print("\nRépartition par catégorie :")
repartition = recommandations["categorie_lift"].value_counts()
for cat, count in repartition.items():
    pct = count / n * 100
    print(f"  {cat:25s} : {count:5d} clients ({pct:.1f}%)")

# ========== Distribution par produit recommandé ==========
print(f"\n{'=' * 60}")
print("DISTRIBUTION DU LIFT PAR PRODUIT RECOMMANDÉ")
print(f"{'=' * 60}")

for produit in recommandations["produit_recommande"].unique():
    sous_ensemble = recommandations[recommandations["produit_recommande"] == produit]
    n_produit = len(sous_ensemble)
    print(f"\n--- {produit} ({n_produit} recommandations) ---")
    print(f"  Lift moyen   : {sous_ensemble['lift'].mean():.2f}")
    print(f"  Lift médian  : {sous_ensemble['lift'].median():.2f}")
    repartition_produit = sous_ensemble["categorie_lift"].value_counts()
    for cat, count in repartition_produit.items():
        pct = count / n_produit * 100
        print(f"  {cat:25s} : {count:5d} ({pct:.1f}%)")

# Sauvegarde pour inspection / réutilisation ultérieure
recommandations.to_csv("recommandations_avec_lift.csv", index=False, encoding="utf-8-sig")
print(f"\nSauvegardé : recommandations_avec_lift.csv (avec colonnes support_global, lift, categorie_lift)")
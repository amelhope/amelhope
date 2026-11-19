"""
Étape 1 : Agrégation niveau compte -> niveau client

Entrée  : clients_synthetiques.csv (1 ligne = 1 compte, plusieurs comptes par client)
Sortie  : clients_aggreges.csv     (1 ligne = 1 client, prêt pour le feature engineering)
"""

import pandas as pd
from datetime import date

df = pd.read_csv("clients_synthetiques.csv", encoding="utf-8-sig")
df["birthday_"] = pd.to_datetime(df["birthday_"])
df["age"] = df["birthday_"].apply(lambda b: date.today().year - b.year)

# Mapping technique -> nom court, plus lisible dans les colonnes finales
NOM_COURT_PRODUIT = {
    "com.bfi.ref.pro.dav.DepositProduct": "deposit",
    "com.bfi.ref.pro.dav.SavingProduct": "saving",
    "com.bfi.ref.pro.dav.LinkedSavingProduct": "linkedsaving",
}
df["produit_court"] = df["product_type"].map(NOM_COURT_PRODUIT)

# ---- 1. Informations qui ne changent pas par client (une valeur par client) ----
infos_client = df.groupby("client_id").agg(
    firstname_=("firstname_", "first"),
    lastname_=("lastname_", "first"),
    age=("age", "first"),
    civilstatus_=("civilstatus_", "first"),
    nombre_enfants=("nombre_enfants", "first"),
    nombre_conjoints=("nombre_conjoints", "first"),
    revenu_mensuel=("revenu_mensuel", "first"),
).reset_index()

# ---- 2. Informations qui dépendent des comptes (à calculer par agrégation) ----
comportement = df.groupby("client_id").agg(
    nombre_comptes_total=("account_id", "count"),
    nombre_types_produits_distincts=("produit_court", "nunique"),
).reset_index()

# ---- 3. Nombre de comptes par type de produit (one-hot count) ----
pivot_produits = (
    df.pivot_table(index="client_id", columns="produit_court",
                    values="account_id", aggfunc="count", fill_value=0)
    .reset_index()
)
pivot_produits.columns.name = None
# renomme pour que ce soit explicite : nb_deposit, nb_saving, nb_linkedsaving
pivot_produits = pivot_produits.rename(
    columns={c: f"nb_{c}" for c in pivot_produits.columns if c != "client_id"}
)

# ---- Fusion des 3 blocs en une seule table client ----
clients_final = (
    infos_client
    .merge(comportement, on="client_id")
    .merge(pivot_produits, on="client_id")
)

clients_final.to_csv("clients_aggreges.csv", index=False, encoding="utf-8-sig")

print(f"{len(clients_final)} clients agrégés (à partir de {len(df)} lignes de comptes)")
print("\nAperçu :")
print(clients_final.head())
print("\nColonnes finales :")
print(clients_final.columns.tolist())
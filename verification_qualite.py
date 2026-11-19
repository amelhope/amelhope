"""
Script de vérification qualité pour clients_synthetiques.csv
(version adaptée : sans la colonne persona, qui n'existe plus
depuis qu'on extrait les données directement de PostgreSQL)
"""

import pandas as pd

df = pd.read_csv("clients_synthetiques.csv", encoding="utf-8-sig")
df["birthday_"] = pd.to_datetime(df["birthday_"])

erreurs = []

# 1. Pas de valeurs manquantes
manquants = df.isna().sum()
if manquants.sum() > 0:
    erreurs.append(f"Valeurs manquantes trouvées:\n{manquants[manquants > 0]}")

# 2. Pas de doublons sur account_id
doublons_compte = df["account_id"].duplicated().sum()
if doublons_compte > 0:
    erreurs.append(f"{doublons_compte} account_id en double !")

# 3. Cohérence civilstatus_ / nombre_conjoints
incoherence_conjoint = df[
    ((df["civilstatus_"] == "Married") & (df["nombre_conjoints"] == 0)) |
    ((df["civilstatus_"] != "Married") & (df["nombre_conjoints"] > 0))
]
if len(incoherence_conjoint) > 0:
    erreurs.append(f"{len(incoherence_conjoint)} lignes où civilstatus_ et nombre_conjoints ne concordent pas")

# 4. product_code / product_type toujours associés correctement
mapping_attendu = {
    "CD001": "com.bfi.ref.pro.dav.DepositProduct",
    "CD002": "com.bfi.ref.pro.dav.DepositProduct",
    "CD006": "com.bfi.ref.pro.dav.LinkedSavingProduct",
    "CD008": "com.bfi.ref.pro.dav.SavingProduct",
}
mauvais_mapping = df[df.apply(lambda r: mapping_attendu.get(r["product_code"]) != r["product_type"], axis=1)]
if len(mauvais_mapping) > 0:
    erreurs.append(f"{len(mauvais_mapping)} lignes où product_code et product_type ne correspondent pas")

# 5. Pas de client_id orphelin (chaque compte a bien un client valide)
if df["client_id"].isna().sum() > 0:
    erreurs.append("Des account_id n'ont pas de client_id associé")

# ---- résumé final ----
print(f"Fichier vérifié : {len(df)} lignes, {df['client_id'].nunique()} clients uniques\n")

if not erreurs:
    print("✅ Aucune anomalie détectée sur l'ensemble du fichier.")
else:
    print(f"⚠️ {len(erreurs)} type(s) de problème détecté(s) :\n")
    for e in erreurs:
        print("-", e, "\n")
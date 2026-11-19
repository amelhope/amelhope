from faker import Faker
from datetime import date
import random
import csv

fake = Faker("fr_FR")

PRODUCTS = {
    "CD001": "com.bfi.ref.pro.dav.DepositProduct",
    "CD006": "com.bfi.ref.pro.dav.LinkedSavingProduct",
    "CD008": "com.bfi.ref.pro.dav.SavingProduct",
}

def determiner_persona(age):
    if age < 26:
        return "Etudiant"
    elif age < 32:
        return "JeuneActif"
    elif age < 50:
        return "Famille"
    elif age < 60:
        return "Premium"
    else:
        return "Senior"

def tirer_revenu(persona):
    fourchettes = {
        "Etudiant": (0, 900), "JeuneActif": (900, 2200),
        "Famille": (1500, 4000), "Premium": (4000, 12000),
        "Senior": (800, 3000),
    }
    minimum, maximum = fourchettes[persona]
    return round(random.uniform(minimum, maximum), 2)

def tirer_civilstatus(persona):
    proba_marie = {
        "Etudiant": 0.05, "JeuneActif": 0.40, "Famille": 0.80,
        "Premium": 0.70, "Senior": 0.50,
    }
    return "Married" if random.random() < proba_marie[persona] else "Single"

def tirer_enfants(civilstatus):
    if civilstatus == "Married" and random.random() < 0.75:
        return random.randint(1, 4)
    elif civilstatus == "Single" and random.random() < 0.15:
        return random.randint(1, 2)
    return 0

def tirer_nb_comptes(persona):
    fourchettes = {
        "Etudiant": (1, 2), "JeuneActif": (2, 4), "Famille": (3, 7),
        "Premium": (5, 12), "Senior": (2, 5),
    }
    minimum, maximum = fourchettes[persona]
    return random.randint(minimum, maximum)

def tirer_produit(persona):
    poids = {
        "Etudiant": {"CD001": 0.7, "CD008": 0.1, "CD006": 0.2},
        "JeuneActif": {"CD001": 0.5, "CD006": 0.3, "CD008": 0.2},
        "Famille": {"CD001": 0.35, "CD006": 0.4, "CD008": 0.25},
        "Premium": {"CD001": 0.3, "CD006": 0.3, "CD008": 0.4},
        "Senior": {"CD001": 0.4, "CD008": 0.5, "CD006": 0.1},
    }
    p = poids[persona]
    return random.choices(list(p.keys()), weights=list(p.values()), k=1)[0]

# ---- génération ----
lignes = []
account_id = 900000

for client_id in range(1, 301):
    prenom = fake.first_name()
    nom = fake.last_name()
    naissance = fake.date_of_birth(minimum_age=18, maximum_age=70)
    age = date.today().year - naissance.year
    persona = determiner_persona(age)
    revenu = tirer_revenu(persona)
    civilstatus = tirer_civilstatus(persona)
    enfants = tirer_enfants(civilstatus)
    conjoints = 1 if civilstatus == "Married" else 0
    nb_comptes = tirer_nb_comptes(persona)

    # une ligne par compte (comme dans le vrai fichier LANALA)
    for _ in range(nb_comptes):
        account_id += 1
        code = tirer_produit(persona)
        lignes.append({
            "client_id": client_id,
            "firstname_": prenom,
            "lastname_": nom,
            "fullname_": f"{prenom} {nom}",
            "birthday_": naissance,
            "civilstatus_": civilstatus,
            "entity_type": "com.bfi.ref.ent.per.Person",
            "account_id": account_id,
            "product_code": code,
            "product_type": PRODUCTS[code],
            "nombre_enfants": enfants,
            "nombre_conjoints": conjoints,
            "revenu_mensuel": revenu,
            "persona": persona,
        })

# encoding="utf-8-sig" -> Excel reconnait automatiquement l'UTF-8 (accents OK)
with open("clients_synthetiques.csv", "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=lignes[0].keys())
    writer.writeheader()
    writer.writerows(lignes)

print(f"Terminé ! {len(lignes)} lignes (comptes) pour 300 clients écrites dans clients_synthetiques.csv")

# ---- vérification rapide ----
import pandas as pd

df = pd.read_csv("clients_synthetiques.csv", encoding="utf-8-sig")

print("\n--- Répartition des personas ---")
print(df["persona"].value_counts())

print("\n--- Revenu moyen par persona ---")
print(df.groupby("persona")["revenu_mensuel"].mean().round(0))

print("\n--- Taux d'enfants par statut civil ---")
print(df.groupby("civilstatus_")["nombre_enfants"].apply(lambda x: (x > 0).mean().round(2)))

print("\n--- Valeurs manquantes par colonne (doit être 0 partout) ---")
print(df.isna().sum())
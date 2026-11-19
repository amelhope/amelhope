import random
from datetime import date, datetime

import numpy as np
import psycopg2
from faker import Faker

fake = Faker("fr_FR")

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    dbname="lanala",
    user="postgres",
    password="lanala2026",
)
conn.autocommit = False
cur = conn.cursor()

PRODUITS = {
    "CD001": "com.bfi.ref.pro.dav.DepositProduct",
    "CD006": "com.bfi.ref.pro.dav.LinkedSavingProduct",
    "CD008": "com.bfi.ref.pro.dav.SavingProduct",
}

PERSONAS = {
    "Etudiant": {
        "poids": 0.15, "age_range": (18, 25), "revenu_range": (0, 900),
        "nb_comptes_range": (1, 2),
        "civilstatus_weights": {"Single": 0.95, "Married": 0.05},
        "enfants_proba": 0.02,
        "produit_weights": {"CD001": 0.7, "CD008": 0.1, "CD006": 0.2},
    },
    "JeuneActif": {
        "poids": 0.25, "age_range": (26, 35), "revenu_range": (900, 2200),
        "nb_comptes_range": (2, 4),
        "civilstatus_weights": {"Single": 0.55, "Married": 0.45},
        "enfants_proba": 0.30,
        "produit_weights": {"CD001": 0.5, "CD006": 0.3, "CD008": 0.2},
    },
    "Famille": {
        "poids": 0.30, "age_range": (32, 50), "revenu_range": (1500, 4000),
        "nb_comptes_range": (3, 7),
        "civilstatus_weights": {"Married": 0.8, "Single": 0.15, "Divorced": 0.05},
        "enfants_proba": 0.85,
        "produit_weights": {"CD001": 0.35, "CD006": 0.4, "CD008": 0.25},
    },
    "Premium": {
        "poids": 0.20, "age_range": (35, 60), "revenu_range": (4000, 12000),
        "nb_comptes_range": (5, 12),
        "civilstatus_weights": {"Married": 0.7, "Single": 0.25, "Divorced": 0.05},
        "enfants_proba": 0.6,
        "produit_weights": {"CD001": 0.3, "CD006": 0.3, "CD008": 0.4},
    },
    "Senior": {
        "poids": 0.10, "age_range": (60, 80), "revenu_range": (800, 3000),
        "nb_comptes_range": (2, 5),
        "civilstatus_weights": {"Married": 0.5, "Single": 0.2, "Widowed": 0.3},
        "enfants_proba": 0.7,
        "produit_weights": {"CD001": 0.4, "CD008": 0.5, "CD006": 0.1},
    },
}


def tirer_persona():
    noms = list(PERSONAS.keys())
    poids = [PERSONAS[n]["poids"] for n in noms]
    return random.choices(noms, weights=poids, k=1)[0]


def tirer_age_et_naissance(persona):
    a_min, a_max = PERSONAS[persona]["age_range"]
    age = int(np.random.triangular(a_min, (a_min + a_max) / 2, a_max))
    naissance = date.today().replace(year=date.today().year - age)
    return age, datetime.combine(naissance, datetime.min.time())


def tirer_revenu(persona):
    r_min, r_max = PERSONAS[persona]["revenu_range"]
    mu = np.log((r_min + r_max) / 2 + 1)
    valeur = np.random.lognormal(mean=mu, sigma=0.35)
    return float(np.clip(valeur, r_min, r_max).round(2))


def tirer_civilstatus(persona):
    w = PERSONAS[persona]["civilstatus_weights"]
    return random.choices(list(w.keys()), weights=list(w.values()), k=1)[0]


def tirer_enfants(persona, civilstatus):
    proba = PERSONAS[persona]["enfants_proba"]
    if civilstatus == "Single":
        proba *= 0.4
    return random.randint(1, 4) if random.random() < proba else 0


def tirer_produits(persona, nb_comptes):
    w = PERSONAS[persona]["produit_weights"]
    return random.choices(list(w.keys()), weights=list(w.values()), k=nb_comptes)


for code, type_produit in PRODUITS.items():
    cur.execute(
        """INSERT INTO lanala_synthetic.productservice (code_, type_)
           VALUES (%s, %s) ON CONFLICT (code_) DO NOTHING""",
        (code, type_produit),
    )

N_CLIENTS = 3000

random.seed(42)
np.random.seed(42)
fake.seed_instance(42)

split_indices = list(range(N_CLIENTS))
random.shuffle(split_indices)
n_train = int(N_CLIENTS * 0.8)
split_map = {}
for i, idx in enumerate(split_indices[:n_train]):
    split_map[idx] = "train"
for i, idx in enumerate(split_indices[n_train:]):
    split_map[idx] = "test"

random.seed(42)
np.random.seed(42)
fake.seed_instance(42)

nb_comptes_total = 0

for client_num in range(N_CLIENTS):
    persona = tirer_persona()
    age, naissance = tirer_age_et_naissance(persona)
    civilstatus = tirer_civilstatus(persona)
    revenu = tirer_revenu(persona)
    enfants = tirer_enfants(persona, civilstatus)
    conjoints = 1 if civilstatus == "Married" else 0

    prenom = fake.first_name()
    nom = fake.last_name()

    cur.execute(
        """INSERT INTO lanala_synthetic.entity
           (firstname_, lastname_, fullname_, birthday_, civilstatus_, type_)
           VALUES (%s, %s, %s, %s, %s, %s)
           RETURNING pk_""",
        (prenom, nom, f"{prenom} {nom}", naissance, civilstatus,
         "com.bfi.ref.ent.per.Person"),
    )
    entity_pk = cur.fetchone()[0]

    if enfants > 0:
        cur.execute(
            """INSERT INTO lanala_synthetic.entityfield (entitypk_, name_, itemvalue_)
               VALUES (%s, %s, %s)""",
            (entity_pk, "Nombre d'enfant", str(enfants)),
        )
    if conjoints > 0:
        cur.execute(
            """INSERT INTO lanala_synthetic.entityfield (entitypk_, name_, itemvalue_)
               VALUES (%s, %s, %s)""",
            (entity_pk, "Nombre de conjoint", str(conjoints)),
        )

    cur.execute(
        """INSERT INTO lanala_synthetic.patrimonials (entitypk_, revenumensuelnet_)
           VALUES (%s, %s)""",
        (entity_pk, revenu),
    )

    nb_min, nb_max = PERSONAS[persona]["nb_comptes_range"]
    nb_comptes = random.randint(nb_min, nb_max)
    for code_produit in tirer_produits(persona, nb_comptes):
        cur.execute(
            """INSERT INTO lanala_synthetic.account (ownerpk_, productcode_)
               VALUES (%s, %s)""",
            (entity_pk, code_produit),
        )
    nb_comptes_total += nb_comptes

conn.commit()
cur.close()
conn.close()

print(f"{N_CLIENTS} clients et {nb_comptes_total} comptes insérés "
      f"dans le schéma lanala_synthetic.")
print(f"\nSplit train/test généré (random_state=42) :")
print(f"  TRAIN : {n_train} clients (80%)")
print(f"  TEST  : {N_CLIENTS - n_train} clients (20%)")
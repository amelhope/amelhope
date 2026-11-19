"""
Récupère les données synthétiques depuis PostgreSQL (schéma lanala_synthetic)
et reconstruit le fichier clients_synthetiques.csv — même structure qu'avant,
mais la source est maintenant la vraie base de données (compatible schéma réel).
"""

import pandas as pd
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    dbname="lanala",
    user="postgres",
    password="lanala2026",
)

requete = """
SELECT
    e.pk_ AS client_id,
    e.firstname_,
    e.lastname_,
    e.fullname_,
    e.birthday_,
    e.civilstatus_,
    e.type_ AS entity_type,
    a.pk_ AS account_id,
    ps.code_ AS product_code,
    ps.type_ AS product_type,
    ef_enfant.itemvalue_ AS nombre_enfants,
    ef_conjoint.itemvalue_ AS nombre_conjoints,
    p.revenumensuelnet_ AS revenu_mensuel
FROM lanala_synthetic.entity e
JOIN lanala_synthetic.account a ON a.ownerpk_ = e.pk_
JOIN lanala_synthetic.productservice ps ON a.productcode_ = ps.code_
LEFT JOIN lanala_synthetic.entityfield ef_enfant
    ON ef_enfant.entitypk_ = e.pk_ AND ef_enfant.name_ = 'Nombre d''enfant'
LEFT JOIN lanala_synthetic.entityfield ef_conjoint
    ON ef_conjoint.entitypk_ = e.pk_ AND ef_conjoint.name_ = 'Nombre de conjoint'
LEFT JOIN lanala_synthetic.patrimonials p ON p.entitypk_ = e.pk_
ORDER BY e.pk_;
"""

df = pd.read_sql(requete, conn)
conn.close()

df["nombre_enfants"] = df["nombre_enfants"].fillna(0).astype(int)
df["nombre_conjoints"] = df["nombre_conjoints"].fillna(0).astype(int)
df["revenu_mensuel"] = df["revenu_mensuel"].fillna(0).astype(float)

df.to_csv("clients_synthetiques.csv", index=False, encoding="utf-8-sig")

print(f"{len(df)} lignes (comptes) extraites depuis PostgreSQL "
      f"pour {df['client_id'].nunique()} clients.")
print("Fichier clients_synthetiques.csv régénéré depuis la base de données.")
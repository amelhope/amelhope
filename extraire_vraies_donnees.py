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
FROM global_def.entity e
JOIN global_def.account a ON a.ownerpk_ = e.pk_
JOIN global_def.productservice ps ON a.productcode_ = ps.code_
LEFT JOIN global_def.entityfield ef_enfant
    ON ef_enfant.entitypk_ = e.pk_ AND ef_enfant.name_ = 'Nombre d''enfant'
LEFT JOIN global_def.entityfield ef_conjoint
    ON ef_conjoint.entitypk_ = e.pk_ AND ef_conjoint.name_ = 'Nombre de conjoint'
LEFT JOIN global_def.patrimonials p ON p.entitypk_ = e.pk_
WHERE e.type_ = 'com.bfi.ref.ent.per.Person'
  AND e.pk_ NOT IN (26,29,35,56,58,60,140,220,226,243,279,293,298,392,412,437,
                     445,455,464,471,473,481,485,492,495,518,532,535,540,544,
                     558,569,575,586,617,624,632,635,639,642,646,662,694,748)
ORDER BY e.pk_;
"""

df = pd.read_sql(requete, conn)
conn.close()

df["nombre_enfants"] = df["nombre_enfants"].fillna(0).astype(int)
df["nombre_conjoints"] = df["nombre_conjoints"].fillna(0).astype(int)
df["revenu_mensuel"] = df["revenu_mensuel"].fillna(0).astype(float)

df.to_csv("clients_synthetiques.csv", index=False, encoding="utf-8-sig")

print(f"{len(df)} lignes (comptes) extraites pour {df['client_id'].nunique()} vrais clients LANALA.")
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    dbname="lanala",
    user="postgres",
    password="lanala2026",
)
cur = conn.cursor()

with open("01_creer_schema.sql", "r", encoding="utf-8") as f:
    sql_content = f.read()

cur.execute(sql_content)
conn.commit()
cur.close()
conn.close()

print("✅ Schéma créé avec succès !")
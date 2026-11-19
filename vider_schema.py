import psycopg2
conn = psycopg2.connect(host="localhost", port=5432, dbname="lanala", user="postgres", password="lanala2026")
cur = conn.cursor()
cur.execute("TRUNCATE lanala_synthetic.account, lanala_synthetic.entityfield, lanala_synthetic.patrimonials, lanala_synthetic.entity RESTART IDENTITY CASCADE;")
conn.commit()
print("Schéma lanala_synthetic vidé.")
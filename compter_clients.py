import psycopg2

conn = psycopg2.connect(host="localhost", port=5432, dbname="lanala", user="postgres", password="lanala2026")
cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM lanala_synthetic.entity")
print(f"Nombre de clients dans lanala_synthetic : {cur.fetchone()[0]}")
conn.close()
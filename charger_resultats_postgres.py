"""
Charge les résultats du pipeline (segments KMeans + recommandations KNN)
depuis les CSV vers PostgreSQL, dans le schéma lanala_synthetic.
A relancer à chaque fois que le pipeline est rejoué, pour garder
la base à jour.
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
cur = conn.cursor()

# --- Vider les anciennes valeurs avant de réinsérer (évite les doublons) ---
cur.execute("TRUNCATE lanala_synthetic.resultats_segments;")
cur.execute("TRUNCATE lanala_synthetic.resultats_recommandations;")

# --- Segments ---
segments = pd.read_csv("clients_avec_segments.csv", encoding="utf-8-sig")
for _, row in segments.iterrows():
    cur.execute(
        "INSERT INTO lanala_synthetic.resultats_segments (client_id, segment) VALUES (%s, %s)",
        (int(row["client_id"]), row["segment"]),
    )

# --- Recommandations ---
recommandations = pd.read_csv("recommandations.csv", encoding="utf-8-sig")
for _, row in recommandations.iterrows():
    cur.execute(
        """INSERT INTO lanala_synthetic.resultats_recommandations
           (client_id, produit_recommande, score_confiance) VALUES (%s, %s, %s)""",
        (int(row["client_id"]), row["produit_recommande"], float(row["score_confiance"])),
    )

conn.commit()
cur.close()
conn.close()

print(f"{len(segments)} segments et {len(recommandations)} recommandations chargés dans PostgreSQL.")
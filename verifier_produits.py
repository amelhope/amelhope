import pandas as pd

df = pd.read_csv("clients_synthetiques.csv", encoding="utf-8-sig")
print(df[["product_code", "product_type"]].drop_duplicates().to_string())
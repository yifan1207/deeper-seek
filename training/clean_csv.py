import pandas as pd

csv_path = "/home/supersketchy/nfs_share/deeper-seek/path_lat_lon_with_embeddings_test.csv"

df = pd.read_csv(csv_path)
print(f"Original rows: {len(df)}")

df_cleaned = df.dropna(subset=["embedding"])
df_cleaned = df_cleaned[df_cleaned["embedding"].str.strip() != ""]
print(f"Cleaned rows: {len(df_cleaned)}")
print(f"Removed rows: {len(df) - len(df_cleaned)}")

df_cleaned.to_csv(csv_path, index=False)
print(f"Saved cleaned CSV to: {csv_path}")
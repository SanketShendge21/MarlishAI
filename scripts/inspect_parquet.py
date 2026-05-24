"""Quick inspection of parquet files to understand schema before building the map."""
import pandas as pd

print("=== Marathi_part_1.parquet ===")
df1 = pd.read_parquet("datasets/Marathi_part_1.parquet")
print(f"Columns: {df1.columns.tolist()}")
print(f"Shape: {df1.shape}")
print(df1.head(5))
print()

print("=== Hinglish_part_1.parquet ===")
df2 = pd.read_parquet("datasets/Hinglish_part_1.parquet")
print(f"Columns: {df2.columns.tolist()}")
print(f"Shape: {df2.shape}")
print(df2.head(5))

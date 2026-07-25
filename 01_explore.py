import pandas as pd

FILE = "data/online_retail_II.xlsx"

print("Loading sheet 1 of 2...")
df1 = pd.read_excel(FILE, sheet_name="Year 2009-2010")
print("Loading sheet 2 of 2...")
df2 = pd.read_excel(FILE, sheet_name="Year 2010-2011")

df = pd.concat([df1, df2], ignore_index=True)

print(f"\nRows: {len(df):,}")
print(f"Columns: {len(df.columns)}")
print(df.dtypes)
print(df.head())

df.to_pickle("data/raw.pkl")
print("\nSaved to data/raw.pkl")
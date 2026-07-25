import pandas as pd

df = pd.read_pickle("data/raw.pkl")

# Stratified sample: take all rows for 40 randomly chosen customers
# so the sample contains complete account histories, not random fragments
customers = df['Customer ID'].dropna().unique()
sample_customers = pd.Series(customers).sample(40, random_state=42)

sample = df[df['Customer ID'].isin(sample_customers)]

# Add some deliberately messy rows: cancellations and non-product codes
extras = df[df['StockCode'].isin(['POST','M','ADJUST','BANK CHARGES'])].head(50)
sample = pd.concat([sample, extras], ignore_index=True)

sample.to_csv("data/sample_for_sheets.csv", index=False)
print(f"Sample rows: {len(sample):,}")
print(f"Sample customers: {sample['Customer ID'].nunique()}")
import pandas as pd

df = pd.read_pickle("data/raw.pkl")

print("=" * 60)
print("DATA QUALITY PROFILE")
print("=" * 60)
print(f"\nTotal rows: {len(df):,}")

print("\n--- MISSING VALUES ---")
missing = df.isnull().sum()
for col, n in missing.items():
    if n > 0:
        print(f"{col}: {n:,} ({n/len(df)*100:.1f}%)")

print("\n--- DUPLICATE ROWS ---")
dupes = df.duplicated().sum()
print(f"Exact duplicates: {dupes:,} ({dupes/len(df)*100:.1f}%)")

print("\n--- QUANTITY ---")
print(f"Negative quantity rows: {(df['Quantity'] < 0).sum():,}")
print(f"Zero quantity rows: {(df['Quantity'] == 0).sum():,}")
print(f"Min: {df['Quantity'].min():,}  Max: {df['Quantity'].max():,}")

print("\n--- PRICE ---")
print(f"Negative price rows: {(df['Price'] < 0).sum():,}")
print(f"Zero price rows: {(df['Price'] == 0).sum():,}")
print(f"Min: {df['Price'].min()}  Max: {df['Price'].max():,}")

print("\n--- INVOICES ---")
df['Invoice'] = df['Invoice'].astype(str)
cancelled = df[df['Invoice'].str.startswith('C')]
print(f"Cancellation invoices (start with 'C'): {len(cancelled):,}")
print(f"Unique invoices: {df['Invoice'].nunique():,}")

print("\n--- CUSTOMERS ---")
print(f"Unique customers: {df['Customer ID'].nunique():,}")
print(f"Rows with no customer ID: {df['Customer ID'].isnull().sum():,}")

print("\n--- PRODUCTS ---")
df['StockCode'] = df['StockCode'].astype(str)
print(f"Unique stock codes: {df['StockCode'].nunique():,}")
print(f"Unique descriptions: {df['Description'].nunique():,}")

print("\n--- NON-PRODUCT STOCK CODES ---")
non_numeric = df[~df['StockCode'].str.match(r'^\d{5}')]['StockCode'].value_counts().head(20)
print(non_numeric)

print("\n--- DATE RANGE ---")
print(f"From: {df['InvoiceDate'].min()}")
print(f"To:   {df['InvoiceDate'].max()}")

print("\n--- COUNTRIES ---")
print(df['Country'].value_counts().head(10))
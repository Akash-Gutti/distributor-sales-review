import pandas as pd

print("Loading raw data...")
df = pd.read_pickle("data/raw.pkl")
log = {}
log['raw_rows'] = len(df)

# --- Normalise types ---
df['Invoice'] = df['Invoice'].astype(str).str.strip()
df['StockCode'] = df['StockCode'].astype(str).str.strip().str.upper()
df['Description'] = df['Description'].astype(str).str.strip().str.upper()
df['Country'] = df['Country'].astype(str).str.strip()

# --- 1. Exact duplicates ---
before = len(df)
df = df.drop_duplicates()
log['duplicates_removed'] = before - len(df)

# --- 2. Missing Customer ID ---
before = len(df)
df = df[df['Customer ID'].notna()]
log['no_customer_id_removed'] = before - len(df)
df['Customer ID'] = df['Customer ID'].astype(int)

# --- 3. Non-product stock codes ---
NON_PRODUCT = {
    'POST', 'DOT', 'M', 'C2', 'D', 'S', 'BANK CHARGES', 'ADJUST', 'ADJUST2',
    'AMAZONFEE', 'CRUK', 'PADS', 'TEST001', 'TEST002', 'B', 'GIFT',
    'SP1002', 'DCGSSGIRL', 'DCGSSBOY'
}
before = len(df)
df = df[~df['StockCode'].isin(NON_PRODUCT)]
df = df[~df['StockCode'].str.startswith('GIFT_')]
df = df[~df['StockCode'].str.startswith('DCGS')]
df = df[~df['StockCode'].str.startswith('ADJUST')]
log['non_product_removed'] = before - len(df)

# --- 4. Zero and negative price ---
before = len(df)
df = df[df['Price'] > 0]
log['bad_price_removed'] = before - len(df)

# --- 5. Description standardisation ---
desc_before = df.groupby('StockCode')['Description'].nunique()
log['codes_with_multiple_desc'] = int((desc_before > 1).sum())

canonical = (df.groupby(['StockCode', 'Description'])
               .size().reset_index(name='n')
               .sort_values(['StockCode', 'n'], ascending=[True, False])
               .drop_duplicates('StockCode')[['StockCode', 'Description']]
               .rename(columns={'Description': 'CanonicalDescription'}))

df = df.merge(canonical, on='StockCode', how='left')
log['descriptions_standardised'] = int(
    (df['Description'] != df['CanonicalDescription']).sum()
)
df['Description'] = df['CanonicalDescription']
df = df.drop(columns=['CanonicalDescription'])

# --- 6. Return flag ---
df['IsReturn'] = df['Invoice'].str.startswith('C')
log['return_lines'] = int(df['IsReturn'].sum())

# --- 7. Derived fields ---
df['Revenue'] = (df['Quantity'] * df['Price']).round(2)
df['InvoiceMonth'] = df['InvoiceDate'].dt.to_period('M').astype(str)

# --- 8. Branch dimension (DERIVED — disclosed in README) ---
REGION_MAP = {
    'United Kingdom': 'UK South', 'EIRE': 'Ireland', 'Germany': 'DACH',
    'France': 'France', 'Netherlands': 'Benelux', 'Spain': 'Iberia',
    'Switzerland': 'DACH', 'Belgium': 'Benelux', 'Portugal': 'Iberia',
    'Australia': 'APAC', 'Italy': 'Southern Europe', 'Sweden': 'Nordics',
    'Norway': 'Nordics', 'Finland': 'Nordics', 'Denmark': 'Nordics',
    'Austria': 'DACH', 'Japan': 'APAC', 'Poland': 'Central Europe',
    'Channel Islands': 'UK South', 'Cyprus': 'Southern Europe',
    'Greece': 'Southern Europe', 'Israel': 'Middle East', 'USA': 'North America',
    'Canada': 'North America', 'Singapore': 'APAC', 'Iceland': 'Nordics',
    'Malta': 'Southern Europe', 'Lithuania': 'Baltics',
    'United Arab Emirates': 'Middle East', 'Lebanon': 'Middle East',
    'Bahrain': 'Middle East', 'Saudi Arabia': 'Middle East',
    'Czech Republic': 'Central Europe', 'Brazil': 'South America',
    'European Community': 'Other', 'RSA': 'Africa', 'Thailand': 'APAC',
    'Korea': 'APAC', 'Nigeria': 'Africa', 'West Indies': 'Other',
    'Unspecified': 'Other', 'Bermuda': 'Other', 'Hong Kong': 'APAC'
}
df['Branch'] = df['Country'].map(REGION_MAP).fillna('Other')

# UK split into two notional branches by customer ID parity (synthetic)
uk_mask = df['Country'] == 'United Kingdom'
df.loc[uk_mask & (df['Customer ID'] % 2 == 0), 'Branch'] = 'UK North'
df.loc[uk_mask & (df['Customer ID'] % 2 == 1), 'Branch'] = 'UK South'

# --- Consolidate 17 branches into 8 for reporting ---
def branch_group(b):
    if b in ('UK South', 'UK North', 'Ireland', 'Benelux', 'France', 'DACH'):
        return b
    if b in ('Nordics', 'Iberia', 'Southern Europe', 'Central Europe', 'Baltics'):
        return 'Rest of Europe'
    return 'International'

df['BranchGroup'] = df['Branch'].apply(branch_group)

# --- Summary log ---
log['clean_rows'] = len(df)
log['unique_customers'] = df['Customer ID'].nunique()
log['unique_products'] = df['StockCode'].nunique()
log['unique_invoices'] = df['Invoice'].nunique()
log['branch_groups'] = df['BranchGroup'].nunique()
log['total_revenue'] = round(df['Revenue'].sum(), 2)
log['date_from'] = str(df['InvoiceDate'].min().date())
log['date_to'] = str(df['InvoiceDate'].max().date())

# --- Save ---
df.to_pickle("data/clean.pkl")
df.to_csv("data/clean.csv", index=False)

print("\n" + "=" * 55)
print("CLEANING LOG")
print("=" * 55)
for k, v in log.items():
    if isinstance(v, (int, float)):
        print(f"{k:32} {v:>18,}")
    else:
        print(f"{k:32} {v:>18}")

pct = (log['raw_rows'] - log['clean_rows']) / log['raw_rows'] * 100
print(f"\nRows removed: {log['raw_rows'] - log['clean_rows']:,} ({pct:.1f}%)")
print(f"Rows retained: {log['clean_rows']:,}")
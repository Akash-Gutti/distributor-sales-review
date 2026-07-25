import os
import pandas as pd
from sqlalchemy import create_engine, text

PASSWORD = os.environ.get("PG_PASSWORD")
if not PASSWORD:
    raise SystemExit("Set PG_PASSWORD first:  $env:PG_PASSWORD=\"your_password\"")

DB = "distributor_sales"
engine = create_engine(
    f"postgresql+psycopg2://postgres:{PASSWORD}@localhost:5432/{DB}"
)

print("Loading clean data...")
df = pd.read_pickle("data/clean.pkl")

df = df.rename(columns={
    'Invoice': 'invoice_no',
    'StockCode': 'stock_code',
    'Description': 'description',
    'Quantity': 'quantity',
    'InvoiceDate': 'invoice_date',
    'Price': 'unit_price',
    'Customer ID': 'customer_id',
    'Country': 'country',
    'IsReturn': 'is_return',
    'Revenue': 'revenue',
    'InvoiceMonth': 'invoice_month',
    'Branch': 'branch',
    'BranchGroup': 'branch_group'
})

print(f"Writing {len(df):,} rows to Postgres...")
df.to_sql('sales', engine, if_exists='replace', index=False,
          chunksize=10000, method='multi')

print("Creating indexes...")
with engine.begin() as conn:
    conn.execute(text("CREATE INDEX idx_customer ON sales(customer_id)"))
    conn.execute(text("CREATE INDEX idx_date ON sales(invoice_date)"))
    conn.execute(text("CREATE INDEX idx_stock ON sales(stock_code)"))
    conn.execute(text("CREATE INDEX idx_branch ON sales(branch_group)"))
    conn.execute(text("CREATE INDEX idx_month ON sales(invoice_month)"))

with engine.connect() as conn:
    n = conn.execute(text("SELECT COUNT(*) FROM sales")).scalar()
    rev = conn.execute(text("SELECT ROUND(SUM(revenue)::numeric,2) FROM sales")).scalar()
    cust = conn.execute(text("SELECT COUNT(DISTINCT customer_id) FROM sales")).scalar()

print("\nVerified in database:")
print(f"  Rows:      {n:,}")
print(f"  Customers: {cust:,}")
print(f"  Revenue:   {rev:,}")
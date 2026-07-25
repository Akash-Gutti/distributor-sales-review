import os
import pandas as pd
from sqlalchemy import create_engine

PASSWORD = os.environ.get("PG_PASSWORD")
if not PASSWORD:
    raise SystemExit("Set PG_PASSWORD first:  $env:PG_PASSWORD=\"your_password\"")

engine = create_engine(
    f"postgresql+psycopg2://postgres:{PASSWORD}@localhost:5432/distributor_sales"
)

os.makedirs("data/looker", exist_ok=True)

queries = {}

queries['monthly_trend'] = """
SELECT
    invoice_month,
    branch_group,
    ROUND(SUM(revenue) FILTER (WHERE NOT is_return)::numeric,2) AS sales,
    ROUND(ABS(SUM(revenue) FILTER (WHERE is_return))::numeric,2) AS returns,
    COUNT(DISTINCT customer_id) AS active_customers,
    COUNT(DISTINCT invoice_no)  AS orders
FROM sales
GROUP BY invoice_month, branch_group
ORDER BY invoice_month, sales DESC
"""

queries['declining_accounts'] = """
WITH yearly AS (
    SELECT customer_id, branch_group,
           CASE WHEN invoice_date < '2010-12-01' THEN 'Y1' ELSE 'Y2' END AS period,
           SUM(revenue) AS revenue, COUNT(DISTINCT invoice_no) AS orders
    FROM sales WHERE NOT is_return
    GROUP BY customer_id, branch_group, period
),
pivoted AS (
    SELECT customer_id, MAX(branch_group) AS branch_group,
           SUM(revenue) FILTER (WHERE period='Y1') AS y1_revenue,
           SUM(revenue) FILTER (WHERE period='Y2') AS y2_revenue,
           SUM(orders)  FILTER (WHERE period='Y1') AS y1_orders,
           SUM(orders)  FILTER (WHERE period='Y2') AS y2_orders
    FROM yearly GROUP BY customer_id
)
SELECT customer_id, branch_group,
       ROUND(y1_revenue::numeric,2) AS y1_revenue,
       ROUND(COALESCE(y2_revenue,0)::numeric,2) AS y2_revenue,
       ROUND((COALESCE(y2_revenue,0)-y1_revenue)::numeric,2) AS change_value,
       ROUND(((COALESCE(y2_revenue,0)-y1_revenue)/y1_revenue*100)::numeric,1) AS change_pct,
       y1_orders, COALESCE(y2_orders,0) AS y2_orders
FROM pivoted
WHERE y1_revenue > 1000 AND COALESCE(y2_revenue,0) < y1_revenue * 0.7
ORDER BY change_value ASC
"""

queries['product_opportunity'] = """
WITH product_stats AS (
    SELECT stock_code, description,
           SUM(quantity) AS units_sold, SUM(revenue) AS revenue,
           AVG(unit_price) AS avg_price,
           COUNT(DISTINCT customer_id) AS customers,
           COUNT(DISTINCT invoice_no) AS orders
    FROM sales
    WHERE NOT is_return AND stock_code ~ '^[0-9]{5}'
      AND description NOT ILIKE '%%ADJUST%%' AND description NOT ILIKE '%%CHARGE%%'
      AND description NOT ILIKE '%%FEE%%' AND description NOT ILIKE '%%POSTAGE%%'
      AND description NOT ILIKE '%%CARRIAGE%%'
    GROUP BY stock_code, description
    HAVING SUM(quantity) > 0 AND COUNT(DISTINCT invoice_no) >= 5
)
SELECT stock_code, description, units_sold,
       ROUND(revenue::numeric,2) AS revenue,
       ROUND(avg_price::numeric,2) AS avg_price,
       customers, orders
FROM product_stats
WHERE avg_price >= 20 AND units_sold < 250
ORDER BY revenue DESC
"""

queries['return_risk'] = """
SELECT customer_id, branch_group,
       COUNT(DISTINCT invoice_no) FILTER (WHERE NOT is_return) AS orders,
       ROUND(SUM(revenue) FILTER (WHERE NOT is_return)::numeric,2) AS gross_sales,
       ROUND(ABS(SUM(revenue) FILTER (WHERE is_return))::numeric,2) AS returns,
       ROUND((ABS(SUM(revenue) FILTER (WHERE is_return))
             / NULLIF(SUM(revenue) FILTER (WHERE NOT is_return),0)*100)::numeric,1) AS return_rate_pct
FROM sales GROUP BY customer_id, branch_group
HAVING SUM(revenue) FILTER (WHERE NOT is_return) > 5000
   AND COUNT(DISTINCT invoice_no) FILTER (WHERE NOT is_return) >= 5
   AND ABS(SUM(revenue) FILTER (WHERE is_return))
       / NULLIF(SUM(revenue) FILTER (WHERE NOT is_return),0) > 0.15
ORDER BY return_rate_pct DESC
"""

queries['branch_summary'] = """
SELECT branch_group,
       COUNT(DISTINCT customer_id) AS customers,
       COUNT(DISTINCT invoice_no)  AS orders,
       ROUND(SUM(revenue) FILTER (WHERE NOT is_return)::numeric,2) AS sales,
       ROUND(ABS(SUM(revenue) FILTER (WHERE is_return))::numeric,2) AS returns
FROM sales GROUP BY branch_group ORDER BY sales DESC
"""

for name, sql in queries.items():
    df = pd.read_sql(sql, engine)
    path = f"data/looker/{name}.csv"
    df.to_csv(path, index=False)
    print(f"{name:22} {len(df):>6,} rows  ->  {path}")
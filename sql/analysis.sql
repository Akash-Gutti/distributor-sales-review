-- ============================================================
-- Distributor Sales Performance Review — Analysis
-- Question: which accounts are quietly declining, and which
-- products carry margin but not volume?
-- ============================================================

-- Q1 — Baseline metrics
SELECT
    COUNT(*)                              AS total_lines,
    COUNT(DISTINCT invoice_no)            AS invoices,
    COUNT(DISTINCT customer_id)           AS customers,
    COUNT(DISTINCT stock_code)            AS products,
    ROUND(SUM(revenue)::numeric,2)                              AS net_revenue,
    ROUND(SUM(revenue) FILTER (WHERE is_return)::numeric,2)     AS returns_value,
    ROUND(SUM(revenue) FILTER (WHERE NOT is_return)::numeric,2) AS sales_value,
    MIN(invoice_date)::date               AS from_date,
    MAX(invoice_date)::date               AS to_date
FROM sales;
-- Result: 794,166 lines | 5,875 customers | net £16.36M
--         (£17.07M sales less £710k returns, 4.2% return rate)


-- Q2 — Declining accounts (year-2 vs year-1, 30%+ drop, £1k+ base)
WITH yearly AS (
    SELECT
        customer_id,
        branch_group,
        CASE WHEN invoice_date < '2010-12-01' THEN 'Y1' ELSE 'Y2' END AS period,
        SUM(revenue) AS revenue,
        COUNT(DISTINCT invoice_no) AS orders
    FROM sales
    WHERE NOT is_return
    GROUP BY customer_id, branch_group, period
),
pivoted AS (
    SELECT
        customer_id,
        MAX(branch_group) AS branch_group,
        SUM(revenue) FILTER (WHERE period='Y1') AS y1_revenue,
        SUM(revenue) FILTER (WHERE period='Y2') AS y2_revenue,
        SUM(orders)  FILTER (WHERE period='Y1') AS y1_orders,
        SUM(orders)  FILTER (WHERE period='Y2') AS y2_orders
    FROM yearly
    GROUP BY customer_id
)
SELECT
    customer_id,
    branch_group,
    ROUND(y1_revenue::numeric,2) AS y1_revenue,
    ROUND(COALESCE(y2_revenue,0)::numeric,2) AS y2_revenue,
    ROUND((COALESCE(y2_revenue,0) - y1_revenue)::numeric,2) AS change_value,
    ROUND(((COALESCE(y2_revenue,0) - y1_revenue) / y1_revenue * 100)::numeric,1) AS change_pct,
    y1_orders,
    COALESCE(y2_orders,0) AS y2_orders
FROM pivoted
WHERE y1_revenue > 1000
  AND COALESCE(y2_revenue,0) < y1_revenue * 0.7
ORDER BY change_value ASC;
-- Result: 899 accounts | £2.21M total decline | top 20 = £530k (24%)


-- Q3 — High-value, low-volume products
-- Thresholds are absolute, not percentile: the price distribution is
-- heavily skewed, so a top-decile cut returned £8 items. £20 is ~4x
-- typical unit price; 250 units over 24 months is ~10/month.
WITH product_stats AS (
    SELECT
        stock_code,
        description,
        SUM(quantity)               AS units_sold,
        SUM(revenue)                AS revenue,
        AVG(unit_price)             AS avg_price,
        COUNT(DISTINCT customer_id) AS customers,
        COUNT(DISTINCT invoice_no)  AS orders
    FROM sales
    WHERE NOT is_return
      AND stock_code ~ '^[0-9]{5}'
      AND description NOT ILIKE '%ADJUST%'
      AND description NOT ILIKE '%CHARGE%'
      AND description NOT ILIKE '%FEE%'
      AND description NOT ILIKE '%POSTAGE%'
      AND description NOT ILIKE '%CARRIAGE%'
    GROUP BY stock_code, description
    HAVING SUM(quantity) > 0
       AND COUNT(DISTINCT invoice_no) >= 5
)
SELECT
    stock_code,
    description,
    units_sold,
    ROUND(revenue::numeric,2)   AS revenue,
    ROUND(avg_price::numeric,2) AS avg_price,
    customers,
    orders
FROM product_stats
WHERE avg_price >= 20
  AND units_sold < 250
ORDER BY revenue DESC;
-- Result: 41 products, concentrated in furniture and large homeware


-- Q4 — Monthly revenue trend by branch (dashboard feed, not a finding)
-- Powers the page-1 time series. Included for completeness.
SELECT
    invoice_month,
    branch_group,
    ROUND(SUM(revenue) FILTER (WHERE NOT is_return)::numeric,2) AS sales,
    ROUND(ABS(SUM(revenue) FILTER (WHERE is_return))::numeric,2) AS returns,
    COUNT(DISTINCT customer_id) AS active_customers,
    COUNT(DISTINCT invoice_no)  AS orders
FROM sales
GROUP BY invoice_month, branch_group
ORDER BY invoice_month, sales DESC;


-- Q5 — Elevated return rates (5+ orders, £5k+ sales, >15% returns)
-- The order floor removes single-order reversal artefacts.
SELECT
    customer_id,
    branch_group,
    COUNT(DISTINCT invoice_no) FILTER (WHERE NOT is_return) AS orders,
    ROUND(SUM(revenue) FILTER (WHERE NOT is_return)::numeric,2) AS gross_sales,
    ROUND(ABS(SUM(revenue) FILTER (WHERE is_return))::numeric,2) AS returns,
    ROUND((ABS(SUM(revenue) FILTER (WHERE is_return))
           / NULLIF(SUM(revenue) FILTER (WHERE NOT is_return),0) * 100)::numeric,1) AS return_rate_pct
FROM sales
GROUP BY customer_id, branch_group
HAVING SUM(revenue) FILTER (WHERE NOT is_return) > 5000
   AND COUNT(DISTINCT invoice_no) FILTER (WHERE NOT is_return) >= 5
   AND ABS(SUM(revenue) FILTER (WHERE is_return))
       / NULLIF(SUM(revenue) FILTER (WHERE NOT is_return),0) > 0.15
ORDER BY return_rate_pct DESC;
-- Result: 14 accounts with sustained elevated return behaviour
# Data Quality Log

## Source

UCI Machine Learning Repository — [Online Retail II](https://archive.ics.uci.edu/dataset/502/online+retail+ii)

UK-based online wholesaler selling giftware to business customers, primarily
retailers and distributors buying for resale. Two sheets covering
1 December 2009 – 9 December 2011.

## Raw data profile

Output of `profile.py` against the unmodified source file.

Total rows: 1,067,371
Columns: 8 (Invoice, StockCode, Description, Quantity, InvoiceDate,
Price, Customer ID, Country)

MISSING VALUES
Description: 4,382 (0.4%)
Customer ID: 243,007 (22.8%)

DUPLICATE ROWS
Exact duplicates: 34,335 (3.2%)

QUANTITY
Negative quantity rows: 22,950
Zero quantity rows: 0
Min: -80,995 Max: 80,995

PRICE
Negative price rows: 5
Zero price rows: 6,202
Min: -53,594.36 Max: 38,970.00

INVOICES
Cancellation invoices (prefix 'C'): 19,494
Unique invoices: 53,628

CUSTOMERS
Unique customers: 5,942
Rows with no customer ID: 243,007

PRODUCTS
Unique stock codes: 5,305
Unique descriptions: 5,698

DATE RANGE
From: 2009-12-01 07:45:00
To: 2011-12-09 12:50:00


## Issues identified

**Missing customer IDs (22.8%).** Nearly a quarter of transactions carry no account
identifier. These appear to be counter or unattributed sales.

**Description count exceeds stock code count.** 5,698 descriptions against 5,305
stock codes means the same product code appears with multiple spellings — casing
differences, trailing whitespace, and variant wording.

**Non-product stock codes.** Twenty codes are not products: `POST`, `DOT`, `M`,
`C2`, `D`, `S`, `BANK CHARGES`, `ADJUST`, `ADJUST2`, `AMAZONFEE`, `CRUK`, `PADS`,
`TEST001`, and codes prefixed `GIFT_` or `DCGS`. These represent shipping, manual
adjustments, bank fees, promotional vouchers and test entries.

**Returns encoded two ways.** Cancellations carry a `C` prefix on the invoice
number and a negative quantity. Sample testing confirmed a 1:1 relationship
(249 cancellation invoices, 249 negative-quantity lines in the 4,996-row sample).

**Extreme quantity values.** The ±80,995 min/max pair is a single bulk order and its
full cancellation, not an outlier requiring treatment.

**Zero and negative prices.** 6,202 zero-price lines (free samples or promotional
items) and 5 negative-price lines (recording errors).

## Post-cleaning profile

Output of `clean.py`.

raw_rows 1,067,371
duplicates_removed 34,335
no_customer_id_removed 235,151
non_product_removed 3,659
bad_price_removed 60
codes_with_multiple_desc 597
descriptions_standardised 49,025
return_lines 17,586
clean_rows 794,166
unique_customers 5,875
unique_products 4,634
unique_invoices 43,879
branches 17
total_revenue 16,359,345.59
date_from 2009-12-01
date_to 2011-12-09

Rows removed: 273,205 (25.6%)
Rows retained: 794,166


## Note on removal counts

Removal counts reflect the order operations were applied and do not sum to the
totals in the raw profile.

Deduplication ran first, removing 34,335 rows — of which 7,856 also lacked a
customer ID. The customer ID filter therefore removed 235,151 rows rather than the
243,007 identified in the raw profile.

The same effect explains the zero-price count. Of 6,202 zero-price rows in the raw
data, 6,142 had already been removed as duplicates or as rows without a customer ID.
Only 60 survived to be caught by the price filter.

Cleaning decisions and their rationale: [`decisions.md`](decisions.md)
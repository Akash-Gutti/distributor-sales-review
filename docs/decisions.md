# Cleaning Decisions

Every transformation applied between the raw source file and the analysis table,
with the reasoning behind it. Rules were prototyped by hand in Google Sheets on a
4,996-row sample before being applied at full scale in `clean.py`.

| # | Issue | Decision | Rationale | Rows affected |
|---|---|---|---|---|
| 1 | Exact duplicate rows | Removed | Identical across all 8 fields including invoice number and timestamp — a data entry artefact, not two separate sales | 34,335 (3.2%) |
| 2 | Missing Customer ID | Excluded from scope | Analysis is account-level; a transaction with no account cannot be attributed to one. Retained in the raw file for reference | 235,151 (22.0%) |
| 3 | Non-product stock codes | Excluded from product analysis | `POST`, `DOT`, `M`, `BANK CHARGES`, `ADJUST`, `AMAZONFEE`, `TEST001` and similar are shipping, fees and adjustments, not sellable products. Including them would distort product-level revenue and price analysis | 3,659 |
| 4 | Zero and negative unit price | Excluded | Zero-price lines generate no revenue and distort price averages; negative prices are recording errors. Most had already been removed at step 2 — see the note in `data_quality_log.md` | 60 |
| 5 | Cancellation invoices (prefix `C`) | Retained, flagged via `IsReturn` | Returns are legitimate business events and a signal of account health. An account with high return volume carries different risk from one with none — deleting them would hide that | 17,586 flagged |
| 6 | Negative quantities | Retained — same population as row 5 | Verified 1:1 with cancellation invoices during sample testing (249 of each). Kept so return value can be netted against gross sales | Same as row 5 |
| 7 | Inconsistent product descriptions | Standardised to the most frequent description per stock code | 597 stock codes carried multiple descriptions — casing, trailing whitespace and wording variants of the same product. Unstandardised, product-level grouping fragments | 49,025 lines across 597 codes |
| 8 | No revenue field in source | Derived `Revenue = Quantity × Price` | Source records quantity and unit price separately; revenue is required for all account and product analysis | All rows |
| 9 | No branch dimension in source | Derived from country groupings; UK split into two notional branches | Source has no branch structure. Regional dimension built from country to demonstrate multi-branch reporting. **Branch assignment is synthetic; all transaction values are real** | All rows |
| 10 | 17 branches too granular for reporting | Consolidated to 8 via `branch_group` | Eleven of the seventeen derived branches carried under £80k revenue each. Long tail grouped into "Rest of Europe" and "International" to keep the dashboard readable | All rows |
| 11 | Sample-based rule development | Cleaning rules prototyped on a 4,996-row stratified sample | Sample drawn as complete account histories for 40 randomly selected customers rather than random rows, so account-level patterns remained intact during rule development | 4,996 sampled |
| 12 | Second-pass filter gap | Added regex and description filters at query level | The initial exclusion list used exact matching and would not have caught variants such as `ADJUST2`. Analysis queries apply a `^[0-9]{5}` stock code pattern and description filters as a defensive second pass | Query-level |

## Decisions deliberately not taken

**Outlier removal.** The ±80,995 quantity extremes are a genuine bulk order and its
cancellation, not corrupt data. Removing them would understate a real customer
relationship.

**Return exclusion.** It would have been simpler to drop all 17,586 return lines.
They are retained because return behaviour turned out to be one of the three
findings — see `findings.md`, Finding 3.

**Imputation of missing customer IDs.** No basis exists in the data for inferring
which account an unattributed transaction belongs to. Excluding them and stating
the exclusion is more honest than filling them.
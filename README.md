# Distributor Sales Performance Review

Which accounts are quietly declining, and which products carry margin but not volume?

**[Dashboard](https://datastudio.google.com/reporting/a1d47190-af85-41b7-8db9-f9ea68706a13)** · **[Findings](docs/findings.md)** · **[SQL](sql/analysis.sql)**

## Summary

Analysis of 794,166 wholesale transactions across 5,875 accounts and 4,634 products,
December 2009 – December 2011. Net revenue £16.36M.

Three findings:
- £2.21M of revenue decline across 899 accounts, with 24% concentrated in just 20
- 41 high-ticket products (£20+ per unit) selling under 250 units — furniture and
  large homeware
- 14 accounts returning over 15% of purchases against a 4.2% book average

## Data

[UCI Online Retail II](https://archive.ics.uci.edu/dataset/502/online+retail+ii) —
real transactions from a UK-based online wholesaler.

**Note on the branch dimension:** the source data has no branch structure. Regional
branches were derived from country groupings, with UK accounts split into two
notional branches to demonstrate multi-branch reporting. All transaction values are
real; branch assignment is synthetic and this is stated wherever branch appears.

## Approach

1. **Profiling** — quantified missing values, duplicates, non-product codes,
   cancellations (`profile.py`)
2. **Prototyping** — cleaning rules developed by hand in Google Sheets on a
   4,996-row stratified sample of complete account histories
3. **Cleaning at scale** — rules applied to the full dataset; 273,205 rows removed
   (25.6%), 49,025 product descriptions standardised across 597 stock codes
   (`clean.py`, `docs/decisions.md`)
4. **Analysis** — PostgreSQL, window functions and cohort comparison
   (`sql/analysis.sql`)
5. **Reporting** — Looker Studio dashboard for self-serve access

## Reproducing

```bash
python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
# download online_retail_II.xlsx to data/
python explore.py && python profile.py && python clean.py
$env:PG_PASSWORD="your_password"
python load_to_postgres.py
python export_for_looker.py
```

## Structure

```
├── explore.py, profile.py, clean.py    # pipeline
├── load_to_postgres.py                 # database load
├── export_for_looker.py                # dashboard extracts
├── sql/analysis.sql                    # analysis queries
├── docs/
│   ├── findings.md                     # results and interpretation
│   ├── decisions.md                    # cleaning decisions and rationale
│   └── data_quality_log.md             # raw data profile
└── data/looker/                        # dashboard source CSVs
```
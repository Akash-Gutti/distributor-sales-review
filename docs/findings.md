# Distributor Sales Performance Review — Findings

**Data:** UCI Online Retail II. UK-based wholesale distributor, 794,166 transaction lines across 5,875 accounts and 4,634 products, December 2009 – December 2011.
**Dashboard:** [https://datastudio.google.com/reporting/a1d47190-af85-41b7-8db9-f9ea68706a13]

---

## Question

Which accounts are quietly declining, and which products carry margin but not volume?

---

## Headline

Net revenue over the period was **£16.36M** (£17.07M gross sales less £710k returns, a 4.2% return rate). Two branches — UK North and UK South — account for **83.7% of revenue** and 91% of accounts.

Three findings warrant action:

1. £2.21M of revenue decline is concentrated in 899 accounts — but 24% of that loss sits in just 20 of them.
2. 41 products carry high unit price but minimal volume, representing unexploited margin.
3. 14 accounts return more than 15% of what they buy, against a 4.2% book average.

---

## Finding 1 — Revenue decline is concentrated, not diffuse

899 accounts declined more than 30% between year one and year two, from a base of at least £1,000. Total decline across them: **£2.21M**.

The distribution matters more than the total. The **top 20 accounts represent £530k — 24% of the entire decline from 2% of the declining accounts.**

| Account | Branch | Y1 | Y2 | Change |
|---|---|---|---|---|
| 14156 | Ireland | £186,510 | £116,560 | −£69,950 (−37.5%) |
| 13694 | UK North | £130,601 | £65,040 | −£65,561 (−50.2%) |
| 16754 | UK North | £63,498 | £2,002 | −£61,495 (−96.8%) |
| 17850 | UK North | £45,818 | £5,391 | −£40,426 (−88.2%) |
| 13093 | UK South | £46,312 | £7,832 | −£38,479 (−83.1%) |

Two distinct patterns appear. Accounts like 14156 declined proportionally — order count fell from 90 to 54 and revenue fell in step, suggesting reduced volume from a still-active customer. Accounts like 16754 fell off a cliff: 28 orders to 1. That is not a soft decline; it is a lost account.

The distinction matters because the two require different responses. A proportional decline is a share-of-wallet problem — the customer is still buying, just less, and the question is what they are buying elsewhere. A cliff is a relationship failure, a competitive loss, or a business that stopped trading, and by the time it shows in the data the recovery window has usually closed.

The practical implication is that a review cycle built around a threshold — flagging every account down 30% — generates 899 names and gets ignored. Ranked by absolute value and split by pattern, it generates two short lists: roughly 20 accounts worth a direct commercial conversation, and a smaller set worth a post-mortem to understand why they were lost without anyone noticing.

---

## Finding 2 — High-ticket products are under-sold

41 products average £20 or more per unit while selling fewer than 250 units across 24 months. The pattern is unambiguous: **furniture and large homeware**.

| Product | Avg price | Units | Revenue | Accounts |
|---|---|---|---|---|
| Vintage Red Kitchen Cabinet | £184.23 | 75 | £12,550 | 45 |
| Vintage Blue Kitchen Cabinet | £214.86 | 45 | £9,290 | 30 |
| Vintage Post Office Cabinet | £77.63 | 123 | £7,955 | 42 |
| Rustic Seventeen Drawer Sideboard | £158.71 | 46 | £7,150 | 29 |
| Love Seat Antique White Metal | £114.02 | 58 | £6,210 | 33 |

For contrast, the volume end of the catalogue sells cutlery sets and wicker baskets at £12–15 across 300–600 units.

The Blue Kitchen Cabinet reached 30 accounts; the Red reached 45 — near-identical products with a 50% difference in distribution. That gap is a question for the sales team, not a data problem.

High-ticket items in a wholesale catalogue tend to under-sell for reasons that have little to do with demand. They carry higher working capital risk for the buyer, they are harder to shift if they do not move, and they often require the customer to commit shelf or floor space rather than shelf inventory. A retailer who will happily order 200 trays on impulse will hesitate over four cabinets.

The next thing to check is whether these products cluster in particular accounts. If the 45 buyers of the Red Cabinet are the same profile as the 30 buyers of the Blue, the gap is a merchandising or awareness issue and the fix is straightforward. If they are entirely different accounts, the products may be serving different segments and the comparison is misleading. That question is answerable from this data and would be the natural second pass.

---

## Finding 3 — Return concentration

Book-wide return rate is 4.2%. Fourteen accounts with five or more orders and £5,000+ in sales exceed 15%.

| Account | Branch | Orders | Sales | Returns | Rate |
|---|---|---|---|---|---|
| 14277 | France | 8 | £16,789 | £12,829 | 76.4% |
| 12931 | UK South | 57 | £92,347 | £20,800 | 22.5% |
| 16754 | UK North | 29 | £65,500 | £10,807 | 16.5% |

12931 is the operationally significant one — 57 orders and £20.8k returned is a sustained pattern, not an incident. 16754 appears here *and* in the declining accounts list, which suggests the two are related.

A high return rate sustained across dozens of orders is rarely a customer problem. It usually points to something upstream: a product that does not match its description, a specification mismatch in how the customer orders, or a fulfilment error that keeps recurring. The cost is not only the credit note — it is the handling, the restocking, and the erosion of a working relationship.

The overlap between 16754's return rate and its near-total revenue collapse is the more interesting signal. It is a plausible sequence: returns accumulate, dissatisfaction builds, the account goes quiet. Whether that is what happened here cannot be established from this data, but it suggests return rate is worth monitoring as a leading indicator of churn rather than as an isolated cost line.

---

## What this analysis cannot tell you

- **No cost data.** Margin is proxied by unit price. A £200 cabinet may carry thinner margin than a £12 tray; without cost of goods, "high-value" means high-ticket, not high-margin.
- **Branch dimension is derived.** The source data has no branch structure. Regions were built from country groupings and UK accounts split into two notional branches to demonstrate multi-branch reporting. Transaction values are real; branch assignment is not.
- **No customer context.** Account 16754's collapse could be insolvency, competitive loss, or a merger. The data shows the what, not the why.
- **Two-year window.** Insufficient to separate genuine decline from normal purchasing cycles in a seasonal business.
- **23% of raw transactions excluded** for having no customer ID. These are real sales, and any conclusion about total market activity would need them.

---

## Method

Cleaning rules were prototyped by hand in Google Sheets on a 4,996-row stratified sample — complete account histories for 40 customers rather than random rows, so account-level patterns survived rule development. Rules were then applied at full scale and loaded to PostgreSQL.

Full cleaning decisions and rationale: [`docs/decisions.md`](decisions.md)
Raw data profile: [`docs/data_quality_log.md`](data_quality_log.md)
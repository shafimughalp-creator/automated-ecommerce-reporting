# Decisions log
# Automated E-commerce Reporting System — Simulated Case Study

_Started: 2026-10-16_
_Dataset: Brazilian E-Commerce Public Dataset by Olist (public, historical)_
_Runtime: Google Colab. Storage: /content/drive/MyDrive/automated-ecommerce-reporting/_
_Disclosure: Simulated portfolio case study. No paying client. Monthly batches
are SIMULATED for repeatability tests and labeled as such._

## 1. Data dictionary

Source: Brazilian E-Commerce Public Dataset by Olist (9 CSVs).
Location on Drive: /content/drive/MyDrive/automated-ecommerce-reporting/data/raw/
Pass 1 loads ONLY the two files below. The other seven are deferred.

| File | One row is | Pass 1 role |
|---|---|---|
| olist_orders_dataset.csv | one order header (id, customer, status, timestamps) | REQUIRED - date source |
| olist_order_payments_dataset.csv | one payment leg on an order (an order can have several) | REQUIRED - value source |
| olist_customers_dataset.csv | one customer record (customer_unique_id is the real person; customer_id is per-order) | Deferred to Pass 2 |
| olist_order_items_dataset.csv | one order line (one product on one order) | Pass 2 (product performance) |
| olist_products_dataset.csv | one product in the catalog | Pass 2 (product performance) |
| olist_sellers_dataset.csv | one seller | Pass 2 (optional) |
| olist_order_reviews_dataset.csv | one review submitted for an order | Pass 2 (optional) |
| olist_geolocation_dataset.csv | one zip-code-prefix geolocation entry | Out of scope |
| product_category_name_translation.csv | one category-name translation (PT to EN) | Pass 2 (with products) |

Minimum files for Pass 1: olist_orders_dataset.csv + olist_order_payments_dataset.csv.

## 2. KPI definitions

Pass 1 uses monthly payment value as the single skeleton KPI.
Other KPIs (order count, AOV, top products, top categories, payment-method share)
are drafted and will be confirmed after the audit at Step 6.

| KPI | Formula | Date field | Exclusions | Grain | Status |
|---|---|---|---|---|---|
| Monthly payment value | SUM(order_payments.payment_value) grouped by month | TBD at Step 6 | TBD at Step 6 | one payment leg, summed to month | Draft |
| Monthly order count | COUNT(DISTINCT order_id) grouped by month | TBD at Step 6 | TBD at Step 6 | one order | Draft |
| Average order value | monthly payment value / monthly order count | TBD at Step 6 | TBD at Step 6 | month | Draft |
| Top product revenue | TBD at Step 6 | TBD at Step 6 | cancelled orders | one order line | Not started |
| Top category revenue | TBD at Step 6 | TBD at Step 6 | cancelled orders | one order line | Not started |
| Payment-method share | SUM(payment_value) by payment_type / total | TBD at Step 6 | TBD at Step 6 | one payment leg | Not started |
| Data-quality rate | failed validation rows / total rows | n/a | n/a | record | Not started |

## 3. Cleaning log
| Issue | Rows affected | Decision | Reason | Impact on totals |
|---|---|---|---|---|
| (to be filled at Step 6) | | | | |

## 4. Client answers and assumptions
| Question | Answer | Source and date |
|---|---|---|
| Project type | Automated Monthly Report Generator | User, 2026-10-16 |
| Simulated or real client | Simulated portfolio case study | User, 2026-10-16 |
| Intended user | Small e-commerce owner / ops manager | User, 2026-10-16 |
| Decisions supported | Restock, revenue trend, payment mix, data quality | User, 2026-10-16 |
| Runtime | Google Colab | User, 2026-10-16 |
| Storage root | /content/drive/MyDrive/automated-ecommerce-reporting/ | User, 2026-10-16 |
| SQL engine | SQLite, only if it earns its place | User, 2026-10-16 |
| Current pass | Pass 1 — Skeleton | User, 2026-10-16 |
| Time limit | End of 2026-10-16 (local time) | User, 2026-10-16 |
| Out of scope | Delivery-performance analysis, ML/forecasting, portal, accounting/inventory app | Project Notes §5 |


### Step 5 — Client checkpoint (final answers)

| # | Question | Final rule applied | Notes |
|---|---|---|---|
| 1 | Which timestamp defines the month? | order_purchase_timestamp. | Chosen over order_delivered_customer_date because the latter is 2,965 rows incomplete and would silently drop non-delivered orders. Alternative (delivered month) recorded for future asks. |
| 2 | Which order_status values count as revenue? | All except canceled and unavailable. Includes delivered, shipped, invoiced, processing, approved, created. | created (5 rows, 688.10 BRL) is a flagged borderline inclusion. Refunds not recorded in the dataset -> revenue is not cash retained. |
| 3 | payment_value <= 0 handling | Keep all 9 rows in payments. Exclude from revenue sums. Print at Step 6. | Zero money impact (sum is 0.00). Logged as a data-quality issue, not a revenue change. |
| 4 | payment_type = not_defined | Label as "Other (unclassified)". | Overlaps with 3 of the 9 zero-value rows. A future increase in this label signals a source-system problem, not a new payment method. |
| 5 | Partial years 2016 and 2018 | Keep all months. Label 2016 and 2018-09/2018-10 as partial coverage. | November 2016 is missing entirely (not just sparse). Any YoY comparison must use Jan-Sep 2017 vs Jan-Sep 2018. |

### Additional limitations arising from Step 5

- Refund status is unknown for canceled and unavailable orders. Revenue = payments received on orders the business did not withdraw. NOT cash retained.
- Borderline status included: created (5 rows, 688.10 BRL). Impact less than 0.005% of total.
- 2016 has only three months of data (Sep, Oct, Dec) and November is absent.
- 2018 is truncated at 2018-10-17. October 2018 has 4 orders total.



### Step 6 — Cleaning result (Pass 1)

Cleaning rules applied (from Step 5):
1. Parse order_purchase_timestamp with explicit format. 0 parse failures.
2. Drop the 9 payment rows with payment_value <= 0 before aggregation. They sum to 0.00.
3. Aggregate payments to one row per order_id (SUM of payment_value per order).
4. Left-join payments onto orders (one row per order).
5. Exclude canceled and unavailable orders from revenue (revenue = 0, reason flagged).
6. Classify each order with a revenue_reason.

Reconciliation:
- raw sum(payment_value):       16,008,872.12 BRL
- minus zero-value rows:         0.00 BRL
- minus canceled + unavailable: 269,735.11 BRL
- clean revenue:                15,739,137.01 BRL
- match within 0.01 BRL:        True

Row counts:
- raw orders:                   99,441
- clean order_revenue:          99,441
- orders with revenue = 0:      1,235 (1,234 excluded by status + 1 genuine no-payments)

revenue_reason distribution:
- included:              98,206 orders; sum 15,739,137.01
- excluded_canceled:        625 orders; sum 0.00
- excluded_unavailable:     609 orders; sum 0.00
- no_payments:                1 order;  sum 0.00

Anomalies recorded:
1. 4 orders have no rows in payments. Of these, 1 is genuine no_payments (delivered, no legs).
   The other 3 are canceled orders whose only payment legs were the zero-value not_defined rows
   dropped before aggregation. Money impact: 0.00.
2. Zero-value payment rows are all exactly 0.00 (9 rows, all voucher or not_defined).
   Excluding them does not change revenue.

Files written:
- data/processed/order_revenue.parquet
- data/processed/order_revenue.csv



### Step 7 (narrow) — Outlier check

Full outlier suite (IQR, Z-score, time-series spikes) deferred to Pass 2. Pass 1 checked only the top of the distribution.

Findings:

- Top 10 orders by revenue: all delivered; values decline smoothly from 13,664.08 to 4,513.32. No cliff that would suggest a data-entry typo.
- Largest order (order_id 03caa2c082116e1d31e67e9ae3700499): one credit_card payment leg of 13,664.08 BRL, 1 installment. Not an aggregation of many legs.
- Monthly concentration: in real-coverage months, the largest single order is at most 2.76% of monthly revenue (2016-10, 2017-02). Concentration risk is low.
- The 100%-share months (2016-09, 2016-12, 2018-09) are partial-coverage months, not concentration problems.
- Distribution: 50th pct = 103.91 BRL; 99th pct = 1,048.18; 99.9th pct = 2,327.00; max = 13,664.08. The tail is shallow and represents <0.1% of orders.

Decision:
- No value was corrected, capped, or excluded.
- Extremes retained (Sacred Rule 6).
- Full outlier suite deferred to Pass 2 with the reason: Pass 1 only required a top-of-distribution check for the single KPI.



### Step 8 — Skipped for Pass 1

Step 8 is conditional: it runs only if a KPI needs a field that does not exist yet.

Pass 1's single KPI is monthly payment value. It uses two fields:
- order_purchase_month (created in Step 6)
- revenue (created in Step 6)

No new fields are required, so Step 8 has nothing to do in Pass 1.

Pass 2 will run Step 8 with a full scope: AOV per month, product-level joins,
payment-method share, and any date-part fields needed for those.



### Step 9 — Key/join verification (Part A) and SQLite decision (Part B)

**Part A — six checks (Gate 3):**
| Check | Result |
|---|---|
| `order_id` unique in clean | PASS — 0 duplicates, 99,441 unique / 99,441 rows |
| Every clean `order_id` in raw orders | PASS — 0 orphans |
| Row count preserved | PASS — 99,441 → 99,441 |
| Revenue reconciles independently (rebuilt from raw) | PASS — max diff = 0.000000 |
| Payments composite key still unique | PASS — 0 duplicates |
| No null revenue in clean | PASS — 0 nulls |

**Gate 3 (Part A): PASSED**

Note: `max |revenue - rebuilt|: 0.000000` is not "under tolerance" — it is zero drift, because both paths use float arithmetic on the same values. Strongest class of reconciliation evidence: the clean file can be rebuilt from raw with no loss.

**Part B — decision: `skip`**

Pass 1 uses a single KPI (monthly payment value) already reconciled two independent ways in Pandas. SQLite adds infrastructure without adding information at this stage. Revisit in Pass 2 when product joins and payment-method breakdowns need multi-table aggregation.

**Three rules established at Step 9:**
1. The strongest reconciliation does not use the pipeline's own output. Method 4 rebuilt revenue from raw payments + orders, ignoring `order_revenue.parquet`, and produced the same total to the cent.
2. Row-count preservation proves the left join did not multiply. 99,441 in, 99,441 out. A payments-side grain error would show ~103,886 rows and inflate every later sum.
3. Zero drift is not a coincidence — it is what arithmetic-only pipelines produce. Any future imputation, rounding, or order-dependent aggregation will break it, and we will notice.



### Scope decision — Pass 1 vs Pass 2 (deliverable checklist)

Pass 1 (today) is the skeleton: one KPI (monthly payment value), proven end-to-end
and reconciled. Pass 2 (later) adds the remaining deliverables on the same clean file.

| # | Deliverable | Pass 1 | Pass 2 |
|---|---|---|---|
| A | Monthly Business Summary | Revenue + orders | Full AOV + trend |
| B | Product & Category Performance | not built | built |
| C | Payment Analysis | not built | built |
| D | Data Quality Report | built | built |
| E | Excel workbook + charts | skeleton | full |
| F | Cleaned data + logs | built | built |
| 7 | Reusable program | skeleton | full |

Deferrals that follow from this decision:
- Step 7 full outlier suite (IQR, Z-score, time-series spikes) → Pass 2.
- Step 8 derived fields → Pass 1 skip, Pass 2 full.
- Step 9 Part B SQLite → per decision above (recommended skip for Pass 1).


### Step 10 — Monthly revenue aggregation (Pass 1)

Grain: one row per `order_purchase_month`. Sorted ascending. 25 rows (2016-09 → 2018-10).

Columns and their meaning:
| Column | Definition | Notes |
|---|---|---|
| `order_purchase_month` | `YYYY-MM` from `order_purchase_timestamp` | same field used throughout Pass 1 |
| `order_count` | every order placed that month | includes revenue = 0 rows; **sum = 99,441** |
| `orders_with_revenue` | orders where `revenue > 0` | removes the status-excluded and no-payment orders from the count; **sum = 98,206** |
| `revenue` | `SUM(revenue)` for the month | canceled and unavailable already zeroed at Step 6; **sum = 15,739,137.01 BRL** |
| `revenue_per_order` | `revenue / order_count` | revenue per order *placed*, NOT average order value. Pass 2 adds true AOV. |
| `coverage_flag` | `full` / `partial_2016` / `partial_2018` | marks months with incomplete raw coverage; 2016 months and 2018-09, 2018-10 |

Naming note: the two columns `order_count` and `orders_with_revenue` were renamed from earlier drafts (`orders`, `revenue_orders`) so a business reader cannot confuse the count of orders placed with the count of orders that earned revenue.

Sanity at Step 10 — the monthly table reconciles against numbers already on the record from Steps 6 and 9:
- 25 monthly rows: PASS
- sum(order_count) = 99,441 (expect 99,441): PASS
- sum(orders_with_revenue) = 98,206 (expect 98,206): PASS
- sum(revenue) = 15,739,137.01 (expect 15,739,137.01): PASS

Files written:
- data/processed/monthly_revenue.csv
- data/processed/monthly_revenue.parquet



### Step 11 — Independent rebuild of the monthly table (Pass 1)

Method: read only the two raw CSVs. Re-applied Step 5/6 rules inline
(drop payment_value <= 0; aggregate to order; left-join; exclude canceled +
unavailable; derive month from raw timestamp). Never opened
order_revenue.parquet or monthly_revenue.parquet for computation.

Result:
- months only in shipped : 0
- months only in rebuilt : 0
- max |shipped - rebuilt| order_count         : 0.000000
- max |shipped - rebuilt| orders_with_revenue : 0.000000
- max |shipped - rebuilt| revenue             : 0.000000
- max |shipped - rebuilt| revenue_per_order   : 0.000000
- months with any mismatch (tol=0.01)         : 0

Verdict: PASSED — monthly table is independently rebuildable from raw.

Implementation note: the first run of this cell crashed in the row-level
mismatch mask because of Python operator precedence — `(a-b).abs() > 0 | (c-d).abs() > 0`
was parsed as a chained comparison. The per-column max-diff numbers were
already computed and correct before the crash; the fix is explicit parentheses
around each comparison.

Teach-back recorded at this step:
> Internal consistency does not guarantee correctness. A consistently-wrong rule (e.g. including canceled orders in revenue) would still sum correctly against itself. Rebuilding from raw with the rule re-derived independently is the only way to catch errors or assumptions that survive the cleaning and aggregation steps.



### Step 12 — Excel workbook + PNG (Pass 1 skeleton)

Deliverables produced:
- output/reports/monthly_revenue.xlsx
- output/reports/monthly_revenue.png

Workbook shape (Pass 1 scope only):
1. Sheet "Monthly Revenue" — 25 rows, 6 columns: Month | Orders | Orders with revenue |
   Revenue (BRL) | Revenue per order (BRL) | Coverage. Bold header, frozen top row,
   sized columns, BRL and integer number formats. One line chart of Revenue by month
   anchored to the right of the table.
2. Sheet "Data Quality" — plain-text summary of the Pass 1 cleaning and exclusions
   (zero-value payments, no-payment orders, status exclusions, created-status flag,
   missing 2016-11, partial coverage, revenue definition, reconciliation evidence).

Design decisions:
- Two sheets, not one: Deliverable D (Data Quality Report) is Pass 1 scope. A workbook
  without it fails the project checklist.
- One chart, on the single Pass 1 KPI. No payment-method pie, no product bars; those
  imply analysis that does not exist yet.
- All 25 months plotted, including partial-coverage months. Partial months use open
  markers in the PNG and are labeled in the Coverage column and in a sheet note.
  Cutting them would hide that 2016-09 to 2016-12 and 2018-09 to 2018-10 exist.
- No merged cells, no logo placeholders, no summary dashboard sheet. Those are Pass 2.

Files sizes at write time:
- monthly_revenue.xlsx : 9,597 bytes
- monthly_revenue.png  : 84,379 bytes



### Step 13 — The program (the deliverable)

Six files written to src/:
- src/load_data.py        (  498 bytes)
- src/validate_data.py    (  954 bytes)
- src/clean_data.py       (1,191 bytes)
- src/analyze_data.py     (1,025 bytes)
- src/generate_report.py  (4,802 bytes)
- src/main.py             (2,803 bytes)

Design:
- Config is an in-code dict/module-level constant set for Pass 1. Pass 2 moves to external config file.
- One responsibility per file. main.py orchestrates.
- Strict validation: refuses to run on missing required columns; exits code 2; writes no report.
- Timestamped run folder per execution: output/runs/YYYY-MM-DD_HHMM/.

Cell A — run on data/input/ (valid):
- exit code 0
- loaded orders 99,441 ; payments 103,886
- clean rows 99,441 ; monthly rows 25
- total revenue 15,739,137.01 ; total orders 99,441
- all match Steps 6, 9, 10, 11

Cell B — run on data/input_broken/ (order_id renamed to orderid):
- exit code 2
- no xlsx, no png written; only run_log.txt
- log line: olist_orders_dataset.csv: missing required column(s): ['order_id']. Refusing to run — incompatible input.
- data/input_broken/ is kept as a permanent regression fixture.

Cell C — independent rebuild of the program's output:
- months only in program : 0
- months only in rebuild : 0
- max |program - rebuilt| order_count         : 0.000000
- max |program - rebuilt| orders_with_revenue : 0.000000
- max |program - rebuilt| revenue             : 0.000000
- max |program - rebuilt| revenue_per_order   : 0.000000
- months with any mismatch (tol=0.01)         : 0
- Verdict: PASSED — program output is independently rebuildable from raw.

Known Pass 2 upgrades (not bugs — scope limits of Pass 1):
1. Validator checks column presence only, not dtypes or row-count emptiness.
2. run_log.txt records counts and totals, but not the exclusion breakdown
   (1,234 canceled/unavailable, 9 zero-value payments, 4 no-payment orders).
   Those are in the Excel Data Quality sheet and in DECISIONS.md.


## 5. Skipped steps
| Step | Reason |
|---|---|
| Step 7 (full: IQR / Z-score / time-series spikes) | Deferred to Pass 2. Pass 1 checked the top of the distribution only. |
| Step 8 (derived fields) | Skipped for Pass 1 only. The single KPI uses fields already created in Step 6. Will run in Pass 2 for AOV, product and payment KPIs. |

## 6. Limitations
- Historical data, not a live client's monthly export.
- Simulated monthly batches; labeled as such.
- No cost data -> no profit claims.
- Delivery performance out of scope.
- Revenue definition and order-status handling deferred to Step 6.

## 7. Open questions
1. Which timestamp defines the month? (purchase / approved / delivered)
2. Which order_status values count as revenue?
3. Are split payments summed at order level or handled differently?
4. Does payment_value include freight?
5. Where exactly on Drive will the Olist raw CSVs live?

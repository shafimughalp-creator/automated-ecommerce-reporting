# Automated E-commerce Reporting System

**One command. Two CSVs in. One reconciled Excel report out.**

A small, honest reporting engine that reads monthly e-commerce exports, validates them, cleans them, and produces a monthly revenue report as an Excel workbook plus a self-contained HTML dashboard. Every total is independently rebuilt from the raw source data and matched to zero drift.

---

## Demo — 60 seconds, no install

Open this Colab notebook, click **Run all**, and watch the pipeline run end to end:

> **[https://colab.research.google.com/drive/13tfkuCEMkEJ5YS7WB7qWKDRmsA_WqNzm?usp=sharing]**

You will see the raw data load, the schema validated, the cleaning applied, the monthly table built, the revenue reconciled, and — at the end — an Excel file written to disk. Download it and open it. It is the deliverable.

---

## What it does

Given two CSV files — an **orders** export and a **payments** export — the program:

1. **Loads** both files into memory.
2. **Validates** the schema. If a required column is missing, the program refuses to run and names the column. It never silently produces a wrong report.
3. **Cleans** the data using the rules documented in `docs/DECISIONS.md` (drop zero-value payment rows, aggregate multi-leg payments to one row per order, exclude `canceled` and `unavailable` orders from revenue).
4. **Aggregates** to one row per month: order count, revenue-bearing order count, revenue, revenue per order, and a coverage flag.
5. **Reconciles** by rebuilding the revenue total directly from raw payments and orders — without using its own cleaned output — and asserts that the two match to zero drift.
6. **Writes** an Excel workbook, a PNG chart, a CSV copy, and a run log into a timestamped folder under `output/runs/`.

The Excel workbook is the client deliverable. The dashboard is a visual companion. The run log and `DECISIONS.md` are the audit trail.

---

## Why you can trust the numbers

Every figure the program produces is independently rebuildable from the raw CSVs alone:

| Layer | How it was verified | Result |
|---|---|---|
| Order-level revenue | Rebuild from raw payments + orders | `max diff = 0.000000` |
| Monthly table (in Pandas) | Rebuild from raw, rules re-derived | `max diff = 0.000000` |
| Monthly table (program output) | Rebuild from raw, rules re-derived | `max diff = 0.000000` |

**Row-count preservation:** 99,441 orders in → 99,441 clean rows out. No join has multiplied rows.
**Total revenue:** 15,739,137.01 BRL across 25 months.
**Total orders:** 99,441.

Zero drift is not an accident. It is what an arithmetic-only pipeline produces when no rounding, imputation, or order-dependent aggregation is applied. Any future change that introduces any of those will break this property, and the reconciliation in the demo will show it.

---

## Project layout

    automated-ecommerce-reporting/
    ├── data/
    │   ├── input/                  # drop your orders + payments CSVs here
    │   ├── raw/                    # the original Olist CSVs, never modified
    │   └── processed/              # cleaned derived data (order_revenue, monthly_revenue)
    ├── output/
    │   ├── reports/                # sample Excel workbook, PNG chart, HTML dashboard
    │   └── runs/
    │       └── YYYY-MM-DD_HHMM/    # one timestamped folder per program run
    ├── src/
    │   ├── main.py                 # runs the pipeline (entry point)
    │   ├── load_data.py            # reads the CSVs
    │   ├── validate_data.py        # strict schema check
    │   ├── clean_data.py           # applies the cleaning rules
    │   ├── analyze_data.py         # aggregates to the monthly table
    │   └── generate_report.py      # writes Excel and PNG
    ├── docs/
    │   └── DECISIONS.md            # every rule, deferral, and reconciliation, on the record
    ├── demo/
    │   └── demo_pipeline.ipynb     # the standalone Colab demo
    └── README.md                   # this file

---

## How to run it

### In Colab (recommended for a quick look)

Open the demo notebook, click **Run all**. Nothing to install.

### Locally

    git clone <this-repo-url>
    cd automated-ecommerce-reporting
    pip install -r requirements.txt
    python src/main.py --input data/input --output output/runs/$(date +%Y-%m-%d_%H%M)

The program requires:

- `olist_orders_dataset.csv` with columns `order_id`, `order_status`, `order_purchase_timestamp`
- `olist_order_payments_dataset.csv` with columns `order_id`, `payment_sequential`, `payment_value`

If any of these columns is missing, the program exits with code 2 and writes a `run_log.txt` naming the missing column. It will not produce a report from bad input.

---

## What it expects from your data

The program is **strict** about schema on purpose. A report built from a silently wrong column looks real but is wrong. Rather than guess, the program refuses.

| File | Required columns |
|---|---|
| Orders | `order_id`, `order_status`, `order_purchase_timestamp` |
| Payments | `order_id`, `payment_sequential`, `payment_value` |

**If your CSV does not match this schema, the program will not run.** It will tell you which column is missing. Adapting to a different schema is a small, scoped piece of work.

---

## Scope — what is built, what is deferred

This is **Pass 1**: the skeleton of the reporting engine, proven on one KPI.

| Deliverable | Pass 1 | Pass 2 |
|---|---|---|
| A. Monthly Business Summary | Revenue + order counts | Full AOV + trend analysis |
| B. Product & Category Performance | not built | planned |
| C. Payment Analysis | not built | planned |
| D. Data Quality Report | Built | Expand |
| E. Excel workbook + charts | Skeleton (2 sheets, 1 chart) | Full styling, more charts |
| F. Cleaned data + logs | Built | Built |
| 7. Reusable program | Six-file engine, strict validation, timestamped runs | External config, tests |

**Nothing in Pass 1 will be thrown away in Pass 2.** Pass 2 extends the same engine.

---

## Known limits (Pass 1)

- **The validator checks column presence only.** It does not check data types, empty files, or malformed dates. A file with the right column names but the wrong contents will be caught mid-clean, not at the schema gate. Pass 2 upgrade.
- **The `run_log.txt` records totals but not the exclusion breakdown.** The 1,234 status-excluded orders, 9 zero-value payments, and 4 no-payment orders are on the Excel Data Quality sheet and in `DECISIONS.md`. Pass 2 upgrade.
- **Historical data, not a live client export.** The demo runs on the public Olist dataset. Simulated monthly batches are labeled as such.
- **Partial coverage months:** 2016-09, 2016-10, 2016-12, 2018-09, 2018-10. November 2016 is absent from the raw data.
- **Not built yet:** AOV as a first-class KPI, product performance, payment analysis, SQLite, external config, automated tests. All deferred to Pass 2, all listed in `DECISIONS.md`.

---

## Where the reasoning lives

Every rule, deferral, and reconciliation in this project is recorded in `docs/DECISIONS.md`. That file is the source of truth for **why** the code does what it does. If you are reviewing this project and something looks arbitrary, the answer is there.

---

## About the data

**Source:** Brazilian E-Commerce Public Dataset by Olist (public, historical). 99,441 orders across 25 calendar months from September 2016 to October 2018.

**Disclosure:** This is a **simulated portfolio demonstration**. No real client engagement. All figures are derived from public data and are labeled as such.

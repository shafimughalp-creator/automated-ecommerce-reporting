"""Entry point. Runs the pipeline end-to-end.

Usage (from PROJECT_ROOT):
    python src/main.py --input data/input --output output/runs/<timestamp>
"""
import argparse, os, sys, json
from datetime import datetime

# Make src/ importable when running as a script
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from load_data import load_orders, load_payments
from validate_data import validate_all, SchemaError
from clean_data import clean
from analyze_data import monthly_summary
from generate_report import write_excel, write_png

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="folder containing the CSVs")
    ap.add_argument("--output", required=True, help="folder to write into")
    args = ap.parse_args()

    os.makedirs(args.output, exist_ok=True)
    log_lines = []
    def log(msg):
        print(msg)
        log_lines.append(msg)

    log(f"run started : {datetime.now().isoformat(timespec='seconds')}")
    log(f"input dir   : {args.input}")
    log(f"output dir  : {args.output}")

    # ---- load ---------------------------------------------------
    orders = load_orders(args.input)
    payments = load_payments(args.input)
    log(f"loaded orders   : {len(orders):,}")
    log(f"loaded payments : {len(payments):,}")

    # ---- validate (strict) -------------------------------------
    try:
        validate_all(orders, payments)
    except SchemaError as e:
        log("VALIDATION FAILED")
        log(str(e))
        with open(os.path.join(args.output, "run_log.txt"), "w") as f:
            f.write("\n".join(log_lines))
        sys.exit(2)
    log("validation      : PASS")

    # ---- clean --------------------------------------------------
    clean_df = clean(orders, payments)
    log(f"clean rows      : {len(clean_df):,}")

    # ---- analyze ------------------------------------------------
    monthly = monthly_summary(clean_df)
    log(f"monthly rows    : {len(monthly)}")
    log(f"total revenue   : {monthly['revenue'].sum():,.2f}")
    log(f"total orders    : {int(monthly['order_count'].sum()):,}")

    # ---- report -------------------------------------------------
    xlsx = os.path.join(args.output, "monthly_revenue.xlsx")
    png  = os.path.join(args.output, "monthly_revenue.png")
    write_excel(monthly, xlsx)
    write_png(monthly, png)
    log(f"wrote           : {xlsx}")
    log(f"wrote           : {png}")

    # also keep the CSV so downstream tools can read the numbers
    csv = os.path.join(args.output, "monthly_revenue.csv")
    monthly.to_csv(csv, index=False)
    log(f"wrote           : {csv}")

    log("run finished OK")
    with open(os.path.join(args.output, "run_log.txt"), "w") as f:
        f.write("\n".join(log_lines))

if __name__ == "__main__":
    main()

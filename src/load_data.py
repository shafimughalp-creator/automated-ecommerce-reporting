"""Load raw CSVs for the reporting pipeline. Read-only."""
import os
import pandas as pd

def load_orders(input_dir):
    return pd.read_csv(
        os.path.join(input_dir, "olist_orders_dataset.csv"),
        dtype={"order_id": str, "customer_id": str},
        encoding="utf-8",
    )

def load_payments(input_dir):
    return pd.read_csv(
        os.path.join(input_dir, "olist_order_payments_dataset.csv"),
        dtype={"order_id": str, "payment_type": str},
        encoding="utf-8",
    )

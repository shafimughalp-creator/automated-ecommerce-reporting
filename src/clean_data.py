"""Apply the Pass 1 cleaning rules. Same logic as Step 6, moved here."""
import pandas as pd

EXCLUDE_STATUSES = {"canceled", "unavailable"}

def clean(orders, payments):
    # Rule: parse purchase timestamp
    orders = orders.copy()
    orders["order_purchase_timestamp"] = pd.to_datetime(
        orders["order_purchase_timestamp"],
        format="%Y-%m-%d %H:%M:%S",
        errors="raise",
    )
    orders["order_purchase_month"] = orders["order_purchase_timestamp"].dt.strftime("%Y-%m")

    # Rule: drop zero-value payments, aggregate to order level
    pay_pos = payments[payments["payment_value"] > 0]
    pay_by_order = (
        pay_pos.groupby("order_id", as_index=False)["payment_value"]
        .sum()
        .rename(columns={"payment_value": "revenue"})
    )

    # Rule: left join payments onto orders
    merged = orders[["order_id", "order_status", "order_purchase_month"]].merge(
        pay_by_order, on="order_id", how="left"
    )
    merged["revenue"] = merged["revenue"].fillna(0.0)

    # Rule: exclude canceled + unavailable
    mask = merged["order_status"].isin(EXCLUDE_STATUSES)
    merged["revenue"] = merged["revenue"].where(~mask, 0.0)

    return merged

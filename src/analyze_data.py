"""Aggregate cleaned data to the monthly reporting table."""
import pandas as pd

def monthly_summary(clean_df):
    monthly = (
        clean_df
        .groupby("order_purchase_month", as_index=False)
        .agg(
            order_count         = ("order_id", "size"),
            orders_with_revenue = ("revenue",  lambda s: int((s > 0).sum())),
            revenue             = ("revenue",  "sum"),
        )
    )
    monthly["revenue_per_order"] = (
        monthly["revenue"] / monthly["order_count"]
    ).round(2)

    def coverage(m):
        if m.startswith("2016"):
            return "partial_2016"
        if m in ("2018-09", "2018-10"):
            return "partial_2018"
        return "full"

    monthly["coverage_flag"] = monthly["order_purchase_month"].map(coverage)
    monthly = monthly[[
        "order_purchase_month", "order_count", "orders_with_revenue",
        "revenue", "revenue_per_order", "coverage_flag",
    ]].sort_values("order_purchase_month").reset_index(drop=True)
    return monthly

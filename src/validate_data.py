"""Strict schema validation. Refuses to run on bad input."""
REQUIRED_SCHEMA = {
    "olist_orders_dataset.csv": [
        "order_id",
        "order_status",
        "order_purchase_timestamp",
    ],
    "olist_order_payments_dataset.csv": [
        "order_id",
        "payment_sequential",
        "payment_value",
    ],
}

class SchemaError(Exception):
    pass

def validate_columns(df, filename):
    """Strict: every required column must be present, exactly named."""
    required = REQUIRED_SCHEMA[filename]
    actual = set(df.columns)
    missing = [c for c in required if c not in actual]
    if missing:
        raise SchemaError(
            f"{filename}: missing required column(s): {missing}. "
            f"Refusing to run — incompatible input."
        )
    return True

def validate_all(orders, payments):
    validate_columns(orders, "olist_orders_dataset.csv")
    validate_columns(payments, "olist_order_payments_dataset.csv")

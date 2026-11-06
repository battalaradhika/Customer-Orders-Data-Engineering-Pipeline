import pandas as pd


def transform_data(orders, run_id, source_file):

    df = orders.copy()

    # Convert date into UTC timestamp
    df["order_date"] = pd.to_datetime(
        df["order_date"],
        utc=True,
        errors="raise"
    )

    # Convert data types
    df["quantity"] = df["quantity"].astype(int)

    df["unit_price"] = df["unit_price"].astype(float)

    # Calculate revenue
    df["total_amount"] = (
        df["quantity"] * df["unit_price"]
    ).round(2)

    # Standardize order status
    df["order_status"] = (
        df["status"]
        .str.strip()
        .str.lower()
    )

    # Add pipeline metadata
    df["run_id"] = run_id

    df["source_file"] = source_file

    return df[
        [
            "order_id",
            "customer_id",
            "order_date",
            "quantity",
            "unit_price",
            "total_amount",
            "order_status",
            "run_id",
            "source_file"
        ]
    ]
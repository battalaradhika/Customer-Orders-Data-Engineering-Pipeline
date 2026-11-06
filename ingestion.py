import pandas as pd

from config import INPUT_DIR


CUSTOMER_COLUMNS = {
    "customer_id",
    "customer_name",
    "email",
    "city",
    "created_at"
}

ORDER_COLUMNS = {
    "order_id",
    "customer_id",
    "order_date",
    "quantity",
    "unit_price",
    "status"
}


def validate_schema(df, expected_columns, entity):

    actual_columns = set(df.columns)

    missing = expected_columns - actual_columns

    unexpected = actual_columns - expected_columns

    if missing or unexpected:

        raise ValueError(
            f"{entity} schema error. "
            f"Missing: {sorted(missing)}. "
            f"Unexpected: {sorted(unexpected)}"
        )


def ingest_data(
    customers_path=None,
    orders_path=None
):

    customers_path = customers_path or INPUT_DIR / "customers.csv"

    orders_path = orders_path or INPUT_DIR / "orders.csv"

    customers = pd.read_csv(customers_path)

    orders = pd.read_csv(orders_path)

    validate_schema(
        customers,
        CUSTOMER_COLUMNS,
        "customers"
    )

    validate_schema(
        orders,
        ORDER_COLUMNS,
        "orders"
    )

    print("Data ingestion completed!")

    return customers, orders
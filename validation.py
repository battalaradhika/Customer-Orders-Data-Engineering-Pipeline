import pandas as pd


def validate_data(customers, orders):

    customer_rejects = []

    order_rejects = []

    # Validate customer records
    valid_customers = []

    seen_customers = set()

    for index, row in customers.iterrows():

        reason = None

        customer_id = row["customer_id"]

        if pd.isna(customer_id):

            reason = "missing_customer_id"

        elif pd.isna(row["customer_name"]) or not str(row["customer_name"]).strip():

            reason = "missing_customer_name"

        elif customer_id in seen_customers:

            reason = "duplicate_customer_id"

        if reason:

            customer_rejects.append({

                "entity": "customers",

                "source_row": index + 2,

                "record": row.to_json(),

                "reason": reason

            })

        else:

            seen_customers.add(customer_id)

            valid_customers.append(row.to_dict())

    valid_customers_df = pd.DataFrame(
        valid_customers,
        columns=customers.columns
    )

    valid_customer_ids = set(
        valid_customers_df["customer_id"].tolist()
    )

    # Validate orders
    valid_orders = []

    seen_orders = set()

    allowed_statuses = {
        "placed",
        "shipped",
        "delivered",
        "cancelled"
    }

    for index, row in orders.iterrows():

        reason = None

        order_id = row["order_id"]

        if (
            pd.isna(order_id)
            or pd.isna(row["customer_id"])
            or pd.isna(row["quantity"])
            or pd.isna(row["unit_price"])
            or pd.isna(row["order_date"])
            or pd.isna(row["status"])
        ):

            reason = "missing_required_field"

        elif order_id in seen_orders:

            reason = "duplicate_order_id"

        elif row["customer_id"] not in valid_customer_ids:

            reason = "unknown_customer_id"

        elif row["quantity"] <= 0:

            reason = "invalid_quantity"

        elif row["unit_price"] < 0:

            reason = "negative_unit_price"

        elif str(row["status"]).strip().lower() not in allowed_statuses:

            reason = "invalid_order_status"

        if not pd.isna(order_id):

            seen_orders.add(order_id)

        if reason:

            order_rejects.append({

                "entity": "orders",

                "source_row": index + 2,

                "record": row.to_json(),

                "reason": reason

            })

        else:

            valid_orders.append(row.to_dict())

    valid_orders_df = pd.DataFrame(
        valid_orders,
        columns=orders.columns
    )

    rejects = pd.DataFrame(
        customer_rejects + order_rejects,
        columns=[
            "entity",
            "source_row",
            "record",
            "reason"
        ]
    )

    return (
        valid_customers_df,
        valid_orders_df,
        rejects
    )
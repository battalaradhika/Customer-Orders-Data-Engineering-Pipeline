import pandas as pd
import random

from datetime import datetime, timedelta, timezone
from pathlib import Path

from config import INPUT_DIR, RANDOM_SEED

def generate_data(
    customers_count=100,
    orders_count=500,
    seed=RANDOM_SEED,
    include_invalid=True
):

    random.seed(seed)

    INPUT_DIR.mkdir(parents=True, exist_ok=True)

    cities = [
        "Hyderabad",
        "Nellore",
        "Chennai",
        "Bangalore",
        "Pune"
    ]

    customers = []

    for customer_id in range(1, customers_count + 1):

        customers.append({

            "customer_id": customer_id,

            "customer_name": f"Customer {customer_id}",

            "email": f"customer{customer_id}@example.com",

            "city": random.choice(cities),

            "created_at": (
                datetime(2025, 1, 1, tzinfo=timezone.utc)
                + timedelta(days=random.randint(0, 300))
            ).isoformat()

        })

    orders = []

    statuses = [
        "placed",
        "shipped",
        "delivered",
        "cancelled"
    ]

    for order_id in range(1, orders_count + 1):

        orders.append({

            "order_id": order_id,

            "customer_id": random.randint(1, customers_count),

            "order_date": (
                datetime(2025, 1, 1, tzinfo=timezone.utc)
                + timedelta(days=random.randint(0, 300))
            ).isoformat(),

            "quantity": random.randint(1, 10),

            "unit_price": round(random.uniform(10, 500), 2),

            "status": random.choice(statuses)

        })

    if include_invalid and orders_count >= 6:

        orders[0]["quantity"] = 0

        orders[1]["customer_id"] = customers_count + 100

        orders[2]["unit_price"] = -10

        orders[3]["order_id"] = orders[4]["order_id"]

        orders[5]["quantity"] = None

    customers_df = pd.DataFrame(customers)

    orders_df = pd.DataFrame(orders)

    customers_df.to_csv(
        INPUT_DIR / "customers.csv",
        index=False
    )

    orders_df.to_csv(
        INPUT_DIR / "orders.csv",
        index=False
    )

    print("Sample data generated successfully!")

    print("Customers:", len(customers_df))

    print("Orders:", len(orders_df))


if __name__ == "__main__":

    generate_data(
        customers_count=100,
        orders_count=500
    )
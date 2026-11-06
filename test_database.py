
import pandas as pd
import pytest

from database import (
    create_tables,
    load_customers,
    load_orders,
    scalar_query
)


def create_customer_data():

    return pd.DataFrame([
        {
            "customer_id": 1,
            "customer_name": "Radhika",
            "email": "radha@example.com",
            "city": "Nellore",
            "created_at": "2025-01-01T00:00:00Z"
        }
    ])


def create_order_data():

    return pd.DataFrame([
        {
            "order_id": 101,
            "customer_id": 1,
            "order_date": pd.Timestamp("2025-02-01"),
            "quantity": 2,
            "unit_price": 100,
            "total_amount": 200,
            "order_status": "placed",
            "run_id": "test_run_001",
            "source_file": "orders.csv"
        }
    ])


def test_create_tables(tmp_path):

    db_path = str(tmp_path / "test.db")

    create_tables(db_path)

    count = scalar_query(
        """
        SELECT COUNT(*)
        FROM sqlite_master
        WHERE type = 'table'
        AND name NOT LIKE 'sqlite_%'
        """,
        db_path
    )

    assert count == 6


def test_load_customers(tmp_path):

    db_path = str(tmp_path / "customers.db")

    create_tables(db_path)

    customers = create_customer_data()

    load_customers(customers, db_path)

    count = scalar_query(
        "SELECT COUNT(*) FROM dim_customers",
        db_path
    )

    assert count == 1


def test_load_orders(tmp_path):

    db_path = str(tmp_path / "orders.db")

    create_tables(db_path)

    customers = create_customer_data()
    orders = create_order_data()

    load_customers(customers, db_path)
    load_orders(orders, db_path)

    count = scalar_query(
        "SELECT COUNT(*) FROM fact_orders",
        db_path
    )

    assert count == 1


def test_idempotent_loading(tmp_path):

    db_path = str(tmp_path / "idempotent.db")

    create_tables(db_path)

    customers = create_customer_data()

    load_customers(customers, db_path)
    load_customers(customers, db_path)

    count = scalar_query(
        "SELECT COUNT(*) FROM dim_customers",
        db_path
    )

    assert count == 1


def test_empty_customer_loading(tmp_path):

    db_path = str(tmp_path / "empty.db")

    create_tables(db_path)

    empty_customers = pd.DataFrame(columns=[
        "customer_id",
        "customer_name",
        "email",
        "city",
        "created_at"
    ])

    load_customers(empty_customers, db_path)

    count = scalar_query(
        "SELECT COUNT(*) FROM dim_customers",
        db_path
    )

    assert count == 0

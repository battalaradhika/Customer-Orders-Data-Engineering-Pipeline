import pandas as pd
import pytest

from validation import validate_data


def create_test_data():

    customers = pd.DataFrame([

        {
            "customer_id": 1,
            "customer_name": "Radhika",
            "email": "radha@example.com",
            "city": "Nellore",
            "created_at": "2025-01-01T00:00:00Z"
        },

        {
            "customer_id": 2,
            "customer_name": "Anu",
            "email": "anu@example.com",
            "city": "Hyderabad",
            "created_at": "2025-01-02T00:00:00Z"
        }

    ])

    orders = pd.DataFrame([

        {
            "order_id": 101,
            "customer_id": 1,
            "order_date": "2025-02-01T00:00:00Z",
            "quantity": 2,
            "unit_price": 100,
            "status": "placed"
        },

        {
            "order_id": 102,
            "customer_id": 999,
            "order_date": "2025-02-01T00:00:00Z",
            "quantity": 2,
            "unit_price": 100,
            "status": "placed"
        },

        {
            "order_id": 103,
            "customer_id": 1,
            "order_date": "2025-02-01T00:00:00Z",
            "quantity": 0,
            "unit_price": 100,
            "status": "placed"
        }

    ])

    return customers, orders


def test_valid_records():

    customers, orders = create_test_data()

    vc, vo, rejects = validate_data(customers, orders)

    assert len(vo) == 1

    assert len(rejects) == 2


def test_empty_orders():

    customers, orders = create_test_data()

    empty_orders = orders.iloc[0:0]

    vc, vo, rejects = validate_data(
        customers,
        empty_orders
    )

    assert len(vo) == 0

    assert len(rejects) == 0


def test_duplicate_order():

    customers, orders = create_test_data()

    orders = pd.concat(
        [orders, orders.iloc[[0]]],
        ignore_index=True
    )

    vc, vo, rejects = validate_data(customers, orders)

    assert "duplicate_order_id" in rejects["reason"].values


def test_missing_customer_name():

    customers, orders = create_test_data()

    customers.loc[0, "customer_name"] = None

    vc, vo, rejects = validate_data(customers, orders)

    assert "missing_customer_name" in rejects["reason"].values
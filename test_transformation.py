import pandas as pd

from transformation import transform_data


def test_revenue_calculation():

    orders = pd.DataFrame([

        {
            "order_id": 101,
            "customer_id": 1,
            "order_date": "2025-01-01T00:00:00Z",
            "quantity": 3,
            "unit_price": 100,
            "status": "PLACED"
        }

    ])

    result = transform_data(
        orders,
        "test-run",
        "orders.csv"
    )

    assert result.iloc[0]["total_amount"] == 300

    assert result.iloc[0]["order_status"] == "placed"

    assert result.iloc[0]["run_id"] == "test-run"
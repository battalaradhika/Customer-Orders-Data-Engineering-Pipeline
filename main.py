import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from config import (
    INPUT_DIR,
    OUTPUT_DIR,
    QUARANTINE_DIR,
    REPORT_DIR,
    DB_PATH
)

from data_generator import generate_data

from ingestion import ingest_data

from validation import validate_data

from transformation import transform_data

from database import (
    create_tables,
    load_customers,
    load_orders,
    save_rejects,
    save_pipeline_run,
    publish_run,
    scalar_query
)

from orchestration import execute_task

from monitoring import (
    setup_logger,
    send_failure_notification
)


def run_pipeline(
    customers_path=None,
    orders_path=None,
    db_path=DB_PATH
):

    logger = setup_logger()

    run_id = str(uuid.uuid4())

    started_at = datetime.now(timezone.utc).isoformat()

    state = {}

    def ingestion_task():

        customers, orders = ingest_data(
            customers_path,
            orders_path
        )

        state["customers"] = customers

        state["orders"] = orders

        state["input_count"] = len(orders)

    def validation_task():

        valid_customers, valid_orders, rejects = validate_data(
            state["customers"],
            state["orders"]
        )

        state["valid_customers"] = valid_customers

        state["valid_orders"] = valid_orders

        state["rejects"] = rejects

        state["rejected_count"] = len(rejects)

        save_rejects(
            rejects,
            run_id,
            db_path
        )

        # Keep rejected records as a separately accessible file.
        if not rejects.empty:

            rejects.to_csv(
                QUARANTINE_DIR / f"{run_id}_rejected.csv",
                index=False
            )

    def transformation_task():

        state["transformed"] = transform_data(
            state["valid_orders"],
            run_id,
            Path(orders_path or INPUT_DIR / "orders.csv").name
        )

    def loading_task():

        load_customers(
            state["valid_customers"],
            db_path
        )

        load_orders(
            state["transformed"],
            db_path
        )

    def reconciliation_task():

        transformed = state["transformed"]

        expected_count = len(transformed)

        actual_count = scalar_query(
            """
            SELECT COUNT(*)
            FROM fact_orders
            WHERE run_id = ?
            """,
            db_path,
            (run_id,)
        )

        expected_revenue = round(
            float(transformed["total_amount"].sum()),
            2
        )

        actual_revenue = scalar_query(
            """
            SELECT ROUND(COALESCE(SUM(total_amount), 0), 2)
            FROM fact_orders
            WHERE run_id = ?
            """,
            db_path,
            (run_id,)
        )

        if actual_count != expected_count:

            raise ValueError(
                f"Row count mismatch: "
                f"expected={expected_count}, actual={actual_count}"
            )

        if abs(actual_revenue - expected_revenue) > 0.01:

            raise ValueError(
                "Revenue reconciliation failed"
            )

        state["output_count"] = actual_count

        state["reconciliation"] = {

            "expected_rows": expected_count,

            "actual_rows": actual_count,

            "expected_revenue": expected_revenue,

            "actual_revenue": actual_revenue,

            "status": "PASSED"

        }

    def publication_task():

        publish_run(
            run_id,
            state["output_count"],
            db_path
        )

        # Save clean analytical output
        state["transformed"].to_csv(
            OUTPUT_DIR / f"{run_id}_clean_orders.csv",
            index=False
        )

        report = {

            "run_id": run_id,

            "status": "SUCCESS",

            "input_rows": state["input_count"],

            "output_rows": state["output_count"],

            "rejected_rows": state["rejected_count"],

            "reconciliation": state["reconciliation"]

        }

        REPORT_DIR.mkdir(parents=True, exist_ok=True)

        with open(
            REPORT_DIR / f"{run_id}_report.json",
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(report, file, indent=4)

    tasks = [

        ("ingestion", ingestion_task, []),

        ("validation", validation_task, ["ingestion"]),

        ("transformation", transformation_task, ["validation"]),

        ("loading", loading_task, ["transformation"]),

        ("reconciliation", reconciliation_task, ["loading"]),

        ("publication", publication_task, ["reconciliation"])

    ]

    task_status = {}

    input_count = 0

    output_count = 0

    rejected_count = 0

    try:

        create_tables(db_path)

        for name, function, dependencies in tasks:

            statuses = [
                task_status[dependency]
                for dependency in dependencies
            ]

            result = execute_task(
                run_id,
                name,
                function,
                statuses,
                db_path=db_path
            )

            task_status[name] = result

            if result != "SUCCESS":

                raise RuntimeError(
                    f"Pipeline stopped because {name} was {result}"
                )

        input_count = state["input_count"]

        output_count = state["output_count"]

        rejected_count = state["rejected_count"]

        status = "SUCCESS"

        error = None

    except Exception as exc:

        logger.exception("Pipeline execution failed")

        status = "FAILED"

        error = str(exc)

        # Ensure incomplete runs are not published.
        task_status["publication"] = task_status.get(
            "publication",
            "BLOCKED"
        )

        send_failure_notification(
            run_id,
            "pipeline",
            error
        )

        input_count = state.get("input_count", 0)

        output_count = state.get("output_count", 0)

        rejected_count = state.get("rejected_count", 0)

    ended_at = datetime.now(timezone.utc).isoformat()

    save_pipeline_run(
        run_id,
        status,
        started_at,
        ended_at,
        input_count,
        output_count,
        rejected_count,
        error,
        db_path
    )

    result = {

        "run_id": run_id,

        "status": status,

        "task_status": task_status,

        "input_rows": input_count,

        "output_rows": output_count,

        "rejected_rows": rejected_count,

        "error": error

    }

    if status == "SUCCESS":

        result["reconciliation"] = state["reconciliation"]

    print(json.dumps(result, indent=4))

    return result


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--generate",
        action="store_true"
    )

    parser.add_argument(
        "--customers",
        type=int,
        default=100
    )

    parser.add_argument(
        "--orders",
        type=int,
        default=500
    )

    args = parser.parse_args()

    if args.generate:

        generate_data(
            customers_count=args.customers,
            orders_count=args.orders
        )

    run_pipeline()
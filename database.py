import sqlite3

from config import DB_PATH


def get_connection(db_path=DB_PATH):

    connection = sqlite3.connect(db_path)

    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def create_tables(db_path=DB_PATH):

    with get_connection(db_path) as conn:

        conn.executescript("""

        CREATE TABLE IF NOT EXISTS dim_customers (

            customer_id INTEGER PRIMARY KEY,

            customer_name TEXT NOT NULL,

            email TEXT,

            city TEXT,

            created_at TEXT

        );

        CREATE TABLE IF NOT EXISTS fact_orders (

            order_id INTEGER PRIMARY KEY,

            customer_id INTEGER NOT NULL,

            order_date TEXT NOT NULL,

            quantity INTEGER NOT NULL CHECK(quantity > 0),

            unit_price REAL NOT NULL CHECK(unit_price >= 0),

            total_amount REAL NOT NULL,

            order_status TEXT NOT NULL,

            run_id TEXT NOT NULL,

            source_file TEXT NOT NULL,

            FOREIGN KEY(customer_id)
                REFERENCES dim_customers(customer_id)

        );

        CREATE TABLE IF NOT EXISTS rejected_records (

            reject_id INTEGER PRIMARY KEY AUTOINCREMENT,

            run_id TEXT NOT NULL,

            entity TEXT NOT NULL,

            source_row INTEGER NOT NULL,

            record TEXT NOT NULL,

            reason TEXT NOT NULL

        );

        CREATE TABLE IF NOT EXISTS pipeline_runs (

            run_id TEXT PRIMARY KEY,

            status TEXT NOT NULL,

            started_at TEXT NOT NULL,

            ended_at TEXT,

            input_count INTEGER DEFAULT 0,

            output_count INTEGER DEFAULT 0,

            rejected_count INTEGER DEFAULT 0,

            error TEXT

        );

        CREATE TABLE IF NOT EXISTS task_runs (

            task_run_id INTEGER PRIMARY KEY AUTOINCREMENT,

            run_id TEXT NOT NULL,

            task_name TEXT NOT NULL,

            status TEXT NOT NULL,

            attempt INTEGER NOT NULL,

            started_at TEXT NOT NULL,

            ended_at TEXT,

            error TEXT

        );

        CREATE TABLE IF NOT EXISTS published_runs (

            run_id TEXT PRIMARY KEY,

            published_at TEXT NOT NULL,

            row_count INTEGER NOT NULL

        );

        """)


def load_customers(customers, db_path=DB_PATH):

    with get_connection(db_path) as conn:

        rows = [

            (
                int(row.customer_id),
                row.customer_name,
                row.email,
                row.city,
                str(row.created_at)
            )

            for row in customers.itertuples(index=False)
        ]

        conn.executemany("""

            INSERT INTO dim_customers

            VALUES (?, ?, ?, ?, ?)

            ON CONFLICT(customer_id) DO UPDATE SET

            customer_name = excluded.customer_name,

            email = excluded.email,

            city = excluded.city,

            created_at = excluded.created_at

        """, rows)


def load_orders(orders, db_path=DB_PATH):

    with get_connection(db_path) as conn:

        rows = [

            (
                int(row.order_id),
                int(row.customer_id),
                row.order_date.isoformat(),
                int(row.quantity),
                float(row.unit_price),
                float(row.total_amount),
                row.order_status,
                row.run_id,
                row.source_file
            )

            for row in orders.itertuples(index=False)
        ]

        conn.executemany("""

            INSERT INTO fact_orders

            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)

            ON CONFLICT(order_id) DO UPDATE SET

            customer_id = excluded.customer_id,

            order_date = excluded.order_date,

            quantity = excluded.quantity,

            unit_price = excluded.unit_price,

            total_amount = excluded.total_amount,

            order_status = excluded.order_status,

            run_id = excluded.run_id,

            source_file = excluded.source_file

        """, rows)


def save_rejects(rejects, run_id, db_path=DB_PATH):

    if rejects.empty:

        return

    with get_connection(db_path) as conn:

        rows = [

            (
                run_id,
                row.entity,
                int(row.source_row),
                row.record,
                row.reason
            )

            for row in rejects.itertuples(index=False)
        ]

        conn.executemany("""

            INSERT INTO rejected_records

            (run_id, entity, source_row, record, reason)

            VALUES (?, ?, ?, ?, ?)

        """, rows)


def save_pipeline_run(
    run_id,
    status,
    started_at,
    ended_at,
    input_count,
    output_count,
    rejected_count,
    error=None,
    db_path=DB_PATH
):

    with get_connection(db_path) as conn:

        conn.execute("""

            INSERT OR REPLACE INTO pipeline_runs

            VALUES (?, ?, ?, ?, ?, ?, ?, ?)

        """, (

            run_id,
            status,
            started_at,
            ended_at,
            input_count,
            output_count,
            rejected_count,
            error

        ))


def save_task_run(
    run_id,
    task_name,
    status,
    attempt,
    started_at,
    ended_at,
    error=None,
    db_path=DB_PATH
):

    with get_connection(db_path) as conn:

        conn.execute("""

            INSERT INTO task_runs

            (run_id, task_name, status, attempt,
             started_at, ended_at, error)

            VALUES (?, ?, ?, ?, ?, ?, ?)

        """, (

            run_id,
            task_name,
            status,
            attempt,
            started_at,
            ended_at,
            error

        ))


def publish_run(run_id, row_count, db_path=DB_PATH):

    from datetime import datetime, timezone

    with get_connection(db_path) as conn:

        conn.execute("""

            INSERT OR IGNORE INTO published_runs

            VALUES (?, ?, ?)

        """, (

            run_id,
            datetime.now(timezone.utc).isoformat(),
            row_count

        ))


def scalar_query(sql, db_path=DB_PATH, params=()):

    with get_connection(db_path) as conn:

       return conn.execute(sql, params).fetchone()[0]
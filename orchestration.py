import time

from datetime import datetime, timezone
from concurrent.futures import (
    ThreadPoolExecutor,
    TimeoutError as FutureTimeout
)

from config import MAX_RETRIES, TASK_TIMEOUT

from database import save_task_run

from monitoring import (
    setup_logger,
    send_failure_notification
)


def current_time():

    return datetime.now(timezone.utc).isoformat()


def execute_task(
    run_id,
    task_name,
    function,
    dependencies=None,
    db_path=None
):

    logger = setup_logger()

    dependencies = dependencies or []

    # Check upstream dependencies
    if any(status != "SUCCESS" for status in dependencies):

        logger.error(
            "%s blocked due to upstream failure",
            task_name
        )

        return "BLOCKED"

    for attempt in range(1, MAX_RETRIES + 1):

        start_time = current_time()

        error = None

        executor = ThreadPoolExecutor(max_workers=1)

        future = executor.submit(function)

        try:

            future.result(timeout=TASK_TIMEOUT)

            executor.shutdown(wait=True)

            save_task_run(
                run_id,
                task_name,
                "SUCCESS",
                attempt,
                start_time,
                current_time(),
                db_path=db_path
            )

            logger.info(
                "%s completed successfully",
                task_name
            )

            return "SUCCESS"

        except FutureTimeout:

            error = f"Task exceeded {TASK_TIMEOUT} seconds"

            future.cancel()

            executor.shutdown(
                wait=False,
                cancel_futures=True
            )

        except Exception as exc:

            error = str(exc)

            executor.shutdown(wait=False)

        status = (
            "RETRYING"
            if attempt < MAX_RETRIES
            else "FAILED"
        )

        save_task_run(
            run_id,
            task_name,
            status,
            attempt,
            start_time,
            current_time(),
            error,
            db_path
        )

        logger.warning(
            "%s failed on attempt %s: %s",
            task_name,
            attempt,
            error
        )

        if attempt < MAX_RETRIES:

            time.sleep(attempt)

    send_failure_notification(
        run_id,
        task_name,
        error
    )

    return "FAILED"
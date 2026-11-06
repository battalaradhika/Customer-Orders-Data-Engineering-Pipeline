import logging

from config import LOG_DIR


def setup_logger():

    logger = logging.getLogger("data_pipeline")

    logger.setLevel(logging.INFO)

    if not logger.handlers:

        file_handler = logging.FileHandler(
            LOG_DIR / "pipeline.log",
            encoding="utf-8"
        )

        console_handler = logging.StreamHandler()

        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s"
        )

        file_handler.setFormatter(formatter)

        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)

        logger.addHandler(console_handler)

    return logger


def send_failure_notification(run_id, task_name, error):

    logger = setup_logger()

    message = (
        f"PIPELINE FAILURE | "
        f"run_id={run_id} | "
        f"task={task_name} | "
        f"error={error}"
    )

    logger.error(message)

    with open(
        LOG_DIR / "failure_notifications.log",
        "a",
        encoding="utf-8"
    ) as file:

        file.write(message + "\n")
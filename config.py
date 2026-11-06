from pathlib import Path

# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Data directories
INPUT_DIR = BASE_DIR / "data" / "input"
OUTPUT_DIR = BASE_DIR / "data" / "output"
QUARANTINE_DIR = BASE_DIR / "data" / "quarantine"

# Monitoring directories
LOG_DIR = BASE_DIR / "logs"
REPORT_DIR = BASE_DIR / "reports"

# Database
DB_PATH = OUTPUT_DIR / "warehouse.db"

# Pipeline configuration
MAX_RETRIES = 3
TASK_TIMEOUT = 60

# Reproducibility
RANDOM_SEED = 42

# Create directories automatically
for directory in [
    INPUT_DIR,
    OUTPUT_DIR,
    QUARANTINE_DIR,
    LOG_DIR,
    REPORT_DIR
]:
    directory.mkdir(parents=True, exist_ok=True)
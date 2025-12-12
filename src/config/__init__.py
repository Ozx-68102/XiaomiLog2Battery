from pathlib import Path

INSTANCE_PATH = Path(__file__).parents[2] / "instance"
TXT_PATH = INSTANCE_PATH / "extracted_txt"
DB_PATH = INSTANCE_PATH / "database.db"

NUMERIC_FIELDS = [
    "estimated_battery_capacity", "last_learned_battery_capacity",
    "min_learned_battery_capacity", "max_learned_battery_capacity",
    "cycle_count", "hardware_capacity"
]

TABLE_FIELDS = [
    "log_capture_time", "phone_brand", "nickname",
    "system_version", "design_capacity"
]
TABLE_FIELDS.extend(NUMERIC_FIELDS)

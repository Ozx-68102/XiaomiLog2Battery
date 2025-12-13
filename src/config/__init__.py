from pathlib import Path

INSTANCE_PATH = Path(__file__).parents[2] / "instance"
TXT_PATH = INSTANCE_PATH / "extracted_txt"
DB_PATH = INSTANCE_PATH / "database.db"

BATTERY_CAPACITY_MAPPING = {
    "Estimated battery capacity": "estimated_battery_capacity",
    "Last learned battery capacity": "last_learned_battery_capacity",
    "Min learned battery capacity": "min_learned_battery_capacity",
    "Max learned battery capacity": "max_learned_battery_capacity"
}
BATTERY_CAPACITY_TYPES = list(BATTERY_CAPACITY_MAPPING.values())

NUMERIC_FIELDS = [
    "cycle_count", "hardware_capacity"
]
NUMERIC_FIELDS.extend(BATTERY_CAPACITY_TYPES)

TABLE_FIELDS = [
    "log_capture_time", "phone_brand", "nickname",
    "system_version", "design_capacity"
]
TABLE_FIELDS.extend(NUMERIC_FIELDS)

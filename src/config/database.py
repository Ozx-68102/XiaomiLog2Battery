BATTERY_CAPACITY_MAPPING = {
    "Estimated battery capacity": "estimated_battery_capacity",
    "Last learned battery capacity": "last_learned_battery_capacity",
    "Min learned battery capacity": "min_learned_battery_capacity",
    "Max learned battery capacity": "max_learned_battery_capacity"
}
BATTERY_CAPACITY_TYPES = list(BATTERY_CAPACITY_MAPPING.values())

BATTERY_NUMERIC_FIELDS = [
    "cycle_count", "hardware_capacity"
]
BATTERY_NUMERIC_FIELDS.extend(BATTERY_CAPACITY_TYPES)

ANALYSIS_RESULTS_FIELDS = [
    "log_capture_time", "phone_brand", "nickname",
    "system_version", "design_capacity"
]
ANALYSIS_RESULTS_FIELDS.extend(BATTERY_NUMERIC_FIELDS)

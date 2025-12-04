from Modules.Database import database as db


class BatteryDataService:
    def __init__(self) -> None:
        self.required_fields = db.TABLE_AR_FIELDS

    def _validate_battery_data(self, data: dict[str, str | int]) -> None:
        """
        Check whether battery data is completed or not.
        :param data: Battery data.
        :return: True if battery data is completed.
        """
        missed_fields = [field for field in self.required_fields if field not in data]
        if missed_fields:
            raise ValueError(f"Missed fields: {", ".join(missed_fields)}")

        numeric_fields = [
            field for field in self.required_fields
            if "battery_capacity" in field or field in ["cycle_count", "hardware_capacity"]
        ]

        type_error = [field for field in numeric_fields if not isinstance(data[field], int)]
        if type_error:
            raise TypeError(f"Field(s) must be int: {", ".join(type_error)}.")
    
    def _validate_battery_data_list(self, data_list: list[dict[str, str | int]]) -> None:
        """
        Validate a list of battery data. Raises exception on first validation failure.
        :param data_list: List of battery data dictionaries.
        :raises ValueError: If any data has missing required fields.
        :raises TypeError: If any data has incorrect field types.
        """
        for i, data in enumerate(data_list):
            try:
                self._validate_battery_data(data)
            except (ValueError, TypeError) as e:
                # re-raise the exception, include the data index information
                log_time = data.get("log_capture_time", f"item_{i}")
                raise type(e)(f"Data validation failed for {log_time}: {str(e)}")


    @staticmethod
    def initialize_battery_data_table() -> None:
        db.init_table_ar()

    def init_battery_data(self, data: dict[str, str | int] | list[dict[str, str | int]]) -> int:
        """
        Initialize table of battery data and save data into it.
        :param data: Battery data.
        :return: True even if only one
        """
        data_list = [data] if isinstance(data, dict) else data

        if not data_list:
            raise ValueError("Empty data.")

        self.initialize_battery_data_table()

        try:
            self._validate_battery_data_list(data_list=data_list)
            counts = db.save_many_iar(data=data_list)
            return counts
        except Exception as e:
            print(f"Initialization Failed: {e}")
            return 0

    @staticmethod
    def get_all_battery_data() ->  list[dict[str, str | int]] | None:
        try:
            return db.get_all_results_far()
        except Exception as e:
            print(f"Failed to get all battery data: {e}")
            return None

    def append_battery_data(self, data: dict[str, str | int] | list[dict[str, str | int]]) -> int:
        """
        Append battery data to the existing table without rebuilding it.
        :param data: Battery data.
        :raise ValueError: When data is empty
        :return: counts of saved records.
        """
        data_list = [data] if isinstance(data, dict) else data

        if not data_list:
            raise ValueError("Empty data.")

        try:
            self._validate_battery_data_list(data_list=data)
            counts = db.save_many_iar(data=data)
            return counts
        except Exception as e:
            print(f"Save Failed: {e}")
            return 0

    @staticmethod
    def get_battery_data_by_time(start: str | None, end: str | None) -> list[dict[str, str | int]] | None:
        try:
            return db.get_results_by_time_range_far(start, end)
        except Exception as e:
            print(f"Failed to get battery data from {start} to {end}: {e}")
            return None

if __name__ == "__main__":
    pass

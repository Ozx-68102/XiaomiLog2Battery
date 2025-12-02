from Modules.Database import init_table_ar, save_data_iar, get_all_results_far, get_results_by_time_range_far, TABLE_AR_FIELDS


class BatteryDataService:
    def __init__(self) -> None:
        self.required_fields = TABLE_AR_FIELDS

    def _validate_battery_data(self, data: dict[str, str | int]) -> bool:
        """
        Check whether battery data is completed or not.
        :param data: Battery data.
        :return: True if battery data is completed.
        """
        missed_fields = [field for field in self.required_fields if field not in data]
        if missed_fields:
            raise ValueError(f"Missed fields: {", ".join(missed_fields)}")

        type_error = []
        numeric_fields = [field for field in self.required_fields if "battery_capacity" in field]
        for field in numeric_fields:
            if not isinstance(data[field], int):
                type_error.append(field)

        if type_error:
            raise TypeError(f"Field(s) must be int: {", ".join(type_error)}.")

        return True

    @staticmethod
    def initialize_battery_data_table() -> None:
        init_table_ar()

    def init_battery_data(self, data: dict[str, str | int] | list[dict[str, str | int]]) -> bool:
        """
        Initialize table of battery data and save data into it.
        :param data: Battery data.
        :return: True even if only one
        """
        data_list = [data] if isinstance(data, dict) else data

        if not data_list:
            raise ValueError("Empty data.")

        self.initialize_battery_data_table()

        saved_successful = []
        for item in data_list:
            try:
                self._validate_battery_data(item)
                record_id = save_data_iar(item)
                saved_successful.append(record_id)
            except Exception as e:
                print(f"Save error: {e}. Log capture time: {item.get("log_capture_time")}")
                continue

        return False if not saved_successful else True

    @staticmethod
    def get_all_battery_data() ->  list[dict[str, str | int]] | None:
        try:
            return get_all_results_far()
        except Exception as e:
            print(f"Failed to get all battery data: {e}")
            return None

    def append_battery_data(self, data: dict[str, str | int] | list[dict[str, str | int]]) -> bool:
        """
        Append battery data to the existing table without rebuilding it.
        :param data: Battery data.
        :raise ValueError: When data is empty
        :return: True if data was saved successfully
        """
        data_list = [data] if isinstance(data, dict) else data

        if not data_list:
            raise ValueError("Empty data.")

        saved_successful = []
        for item in data_list:
            try:
                self._validate_battery_data(item)
                record_id = save_data_iar(item)
                saved_successful.append(record_id)
            except Exception as e:
                print(f"Save error: {e}. Log capture time: {item.get("log_capture_time")}")
                continue

        return False if not saved_successful else True

    @staticmethod
    def get_battery_data_by_time(start: str | None, end: str | None) -> list[dict[str, str | int]] | None:
        try:
            return get_results_by_time_range_far(start, end)
        except Exception as e:
            print(f"Failed to get battery data from {start} to {end}: {e}")
            return None

if __name__ == "__main__":
    pass

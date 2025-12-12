from src.config import NUMERIC_FIELDS, TABLE_FIELDS
from src.persistence import init_table, save_data, get_all_results


class DataServices:
    def __init__(self):
        self.numeric_fields = NUMERIC_FIELDS
        self.whole_fields = TABLE_FIELDS

    def __validate_battery_data(self, data: dict[str, str | int]) -> None:
        missed_fields = [field for field in self.whole_fields if field not in data]
        if missed_fields:
            raise Exception(f"Missed fields: {", ".join(missed_fields)}")

        type_error_fields = [field for field in self.numeric_fields if not isinstance(data[field], int)]
        if type_error_fields:
            raise Exception(f"Field(s) must be int: {", ".join(type_error_fields)}.")

    def _data_validator(self, data_list: list[dict[str, str | int]]) -> None:
        """
        Validate a list of battery data.

        Parameters
        ----------
        data_list: list[dict[str, str | int]]
            A list of battery data dictionaries.

        Raises
        -------
        ValueError
            If data has incorrect field types or lack of required fields.
        """
        errors = []
        for i, data in enumerate(data_list, start=1):
            try:
                self.__validate_battery_data(data)
            except Exception as e:
                log_time = data.get("log_capture_time")
                errors.append(f"    [File {i}] LogTime {log_time}: {str(e)}")
                continue

        if errors:
            all_errors = "\n".join(errors)
            raise ValueError(
                f"Data validation failed with {len(errors)} errors: \n"
                f"{all_errors}"
            )

    def _save_battery_data(self, data: list[dict[str, str | int]]) -> int:
        self._data_validator(data_list=data)
        return save_data(data=data)

    def init_battery_data(self, data: dict[str, str | int] | list[dict[str, str | int]]) -> int:
        """
        Initialize table of battery data and save data into it.
        If table exists, it will be deleted and recreated.

        Parameters
        ----------
        data: dict[str, str | int] or list[dict[str, str | int]]
            Battery data.

        Raises
        -------
        ValueError
            If data has incorrect field types or lack of required fields.

        Returns
        -------
        int
            Number of battery data saved.
        """

        data_list = [data] if isinstance(data, dict) else data
        if not data_list:
            raise ValueError("Data is empty.")

        init_table()
        return self._save_battery_data(data=data_list)

    def append_battery_data(self, data: dict[str, str | int] | list[dict[str, str | int]]) -> int:
        """
        Append battery data to the existing table.

        Parameters
        ----------
        data: dict[str, str | int] or list[dict[str, str | int]]
            Battery data.

        Raises
        -------
        ValueError
            If data has incorrect field types or lack of required fields.

        Returns
        -------
        int
            Number of battery data saved.
        """
        data_list = [data] if isinstance(data, dict) else data
        if not data_list:
            raise ValueError("Data is empty.")

        return self._save_battery_data(data=data_list)

    @staticmethod
    def get_all_battery_data() -> list[dict[str, str | int]] | None:
        return get_all_results()


if __name__ == "__main__":
    pass

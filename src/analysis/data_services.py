from typing import Literal

from src.config import BATTERY_NUMERIC_FIELDS, ANALYSIS_RESULTS_FIELDS
from src.persistence import AnalysisResults

type Table = Literal["analysis_results"]


class DataServices:
    def __init__(self):
        self.bat_numeric_fields = BATTERY_NUMERIC_FIELDS
        self.bat_whole_fields = ANALYSIS_RESULTS_FIELDS

        self.AR = AnalysisResults()

    def __val_bat_info(self, data: dict[str, str | int]) -> None:
        missed_fields = [field for field in self.bat_whole_fields if field not in data.keys()]
        if missed_fields:
            raise Exception(f"Missed fields: {", ".join(missed_fields)}")

        type_error_fields = [field for field in self.bat_numeric_fields if not isinstance(data[field], int)]
        if type_error_fields:
            raise Exception(f"Field(s) must be int: {", ".join(type_error_fields)}.")

    def _battery_data_validator(self, data_list: list[dict[str, str | int]]) -> None:
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
                self.__val_bat_info(data=data)
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


    def init_data(self, table: Table, data: dict[str, str | int] | list[dict[str, str | int]]) -> int:
        """
        Initialize table and save data into it.
        If table exists, it will be dropped and recreated.

        Raises
        -------
        ValueError
            If data has incorrect field types or lack of required fields.

        Returns
        -------
        int
            The number of data saved successfully.
        """

        data_list = [data] if isinstance(data, dict) else data
        if not data_list:
            raise ValueError("Data is empty.")

        if table == "analysis_results":
            self._battery_data_validator(data_list=data_list)

            self.AR.init_table()
            return self.AR.save_data(data=data_list)

        raise ValueError("Invalid table name.")

    def append_data(self, table: Table, data: dict[str, str | int] | list[dict[str, str | int]]) -> int:
        """
        Append battery data to the existing table.

        Raises
        -------
        ValueError
            If data has incorrect field types or lack of required fields.

        Returns
        -------
        int
            The number of data saved successfully.
        """
        data_list = [data] if isinstance(data, dict) else data
        if not data_list:
            raise ValueError("Data is empty.")

        if table == "analysis_results":
            self._battery_data_validator(data_list=data_list)
            return self.AR.save_data(data=data_list)

        raise ValueError("Invalid table name.")

    def get_battery_data(self, table: Table, model: str | None = None) -> list[dict[str, str | int]] | None:
        if table == "analysis_results":
            return self.AR.get_results(model=model)

        raise ValueError("Invalid table name.")

    def get_model(self) -> list[str] | None:
        return self.AR.get_unique_model()


if __name__ == "__main__":
    pass

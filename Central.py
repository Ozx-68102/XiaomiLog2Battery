import os
from logging import Logger
from typing import Literal

from Modules.FileProcess import BatteryLoggingExtractor, FolderOperator
from Modules.DataAnalysis import Recording, Searching, Visualizing
from Modules.LogRecord import Log


class ErrorChecker:
    def __init__(self, logs):
        self.log = logs

    def check(self, data: str | list | bool | None, typ: Literal["compressed file", "Xiaomi log file", "battery information", "csv file", "line chart"]) -> None:
        """ Check that the variables received by the main program are as expected, log them and terminate the program if necessary. """
        try:
            valid_types = ["compressed file", "Xiaomi log file", "battery information", "csv file", "line chart"]
            if typ not in valid_types:
                raise ValueError(f"'typ' must be one of {', '.join(valid_types)}, not '{typ}'.")

            if data is None:
                self._log_and_exit(f"No {typ} was found.")
            elif isinstance(data, str):
                self._check_string(data, typ)
            elif isinstance(data, list):
                self._check_list(data, typ)
            elif isinstance(data, bool):
                self._check_boolean(data, typ)
            else:
                raise ValueError(f"Variable 'data' must be a list, string, or boolean, not '{type(data).__name__}'.")
        except ValueError as e:
            self._log_and_exit(str(e))

    def _check_string(self, data: str, typ: str) -> None:
        if typ != "csv file":
            raise ValueError(f"When the type of 'data' is a string, 'typ' must be 'csv file', not '{typ}'.")
        if not data.strip():
            self._log_and_exit(f"No {typ} was created.")
        self.log.debug(f"1 {typ} was created.")

    def _check_list(self, data: list, typ: str) -> None:
        count = len(data)
        if typ == "line chart":
            count_true = sum(1 for item in data if item)
            count_false = count - count_true
            self.log.info(f"{count_true} file(s) visualized successfully, {count_false} file(s) failed.")
        elif typ == "csv file":
            if count == 0:
                self._log_and_exit(f"No {typ} was created.")
            self.log.debug(f"{count} {typ}(s) created.")
        elif typ == "battery information":
            if count > 0:
                self.log.debug(f"Found {count} battery information.")
            else:
                self._log_and_exit(f"No {typ} was found.")
        elif typ == "Xiaomi log file":
            if count > 0:
                self.log.info(f"Successfully extracted {count} Xiaomi log file(s).")
                self.log.debug(f"Found {count} Xiaomi log files.")
            else:
                self._log_and_exit(f"No {typ} was found.")
        else:
            if count > 0:
                self.log.debug(f"Found {count} {typ}(s).")
            else:
                self._log_and_exit(f"No {typ} was found.")

    def _check_boolean(self, data: bool, typ: str) -> None:
        if typ != "line chart":
            raise ValueError(f"When the type of 'data' is a boolean, 'typ' must be 'line chart', not '{typ}'.")
        if not data:
            self._log_and_exit("Failed to visualize battery information.")

    def _log_and_exit(self, message: str) -> None:
        self.log.error(message)
        exit(1)


def main(cr, logger: Log):
    checker = ErrorChecker(logger)

    folder_operator = FolderOperator(cr)
    compressed_files = folder_operator.file_recognition(os.path.join(cr, "zips"))
    checker.check(compressed_files, "compressed file")

    logger.info("Preparing to extract log file(s). Please wait...")
    battery_log_extractor = BatteryLoggingExtractor(cr)
    xiaomi_log = battery_log_extractor.find_xiaomi_log(battery_log_extractor.compress_xiaomi_log(compressed_files))
    checker.check(xiaomi_log, "Xiaomi log file")

    logger.info("Preparing to search information in log file(s). Please wait...")
    searcher = Searching(cr)
    battery_info = searcher.search_info(xiaomi_log)
    checker.check(battery_info, "battery information")

    unique_nicknames = {info["nickname"] for info in battery_info}

    logger.info("Preparing to process data. Please wait...")
    data_recorder = Recording(cr)
    csv_files = data_recorder.create_csv(unique_nicknames)
    checker.check(csv_files, "csv file")

    processed_csv_files = data_recorder.data_processing(battery_info, csv_files)
    checker.check(processed_csv_files, "csv file")

    logger.info("Preparing to visualize data. Please wait...")
    visualizer = Visualizing(cr)
    line_chart_creation_results = [visualizer.pline_chart(csv_file) for csv_file in csv_files]
    checker.check(line_chart_creation_results, "line chart")


if __name__ == "__main__":
    current = os.getcwd()
    log_path = os.path.join(current, "Log")
    os.makedirs(log_path, exist_ok=True)
    log_filename = os.path.join(log_path, "Central.txt")
    log = Log(log_filename)
    log.info("Starting running the program now.")
    log.debug("Log module has been initialled successfully.")
    main(current, log)

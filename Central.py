import os
from typing import Literal

from Modules.DataAnalysis import Recording, Searching, Visualizing
from Modules.FileProcess import BatteryLoggingExtractor, FolderOperator
from Modules.LogRecord import Log


class ErrorChecker:
    def __init__(self, logs):
        self.log = logs

    def check(self, data: str | list | None,
              typ: Literal["compressed file", "Xiaomi log file", "battery information", "csv file", "charts"]) -> None:
        """ Check that the variables received by the main program are as expected, log them and terminate the program if necessary. """
        try:
            valid_types = ["compressed file", "Xiaomi log file", "battery information", "csv file", "charts"]
            if typ not in valid_types:
                raise ValueError(f"'typ' must be one of {', '.join(valid_types)}, not '{typ}'.")

            if data is None:
                self._log_and_exit(f"No {typ} was found.")
            elif isinstance(data, str):
                self._check_string(data, typ)
            elif isinstance(data, list):
                self._check_list(data, typ)
            else:
                raise ValueError(f"Variable 'data' must be a list, string, not '{type(data).__name__}'.")
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
        if typ == "charts":
            count_success = data[0]
            count_failure = data[1]
            if count_success == count_failure == 0:
                self._log_and_exit("Failed to visualize any data.")
            else:
                self.log.info(f"{count_success} data visualized successfully, and {count_failure} failed.")
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

    def _log_and_exit(self, message: str) -> None:
        self.log.error(message)
        exit(1)


def initialize(cr: str, logger: Log) -> None:
    checker = ErrorChecker(logger)

    folder_operator = FolderOperator()
    compressed_files = folder_operator.file_recognition(os.path.join(cr, "zips"))
    checker.check(data=compressed_files, typ="compressed file")

    logger.info("Preparing to extract log file(s). Please wait...")
    battery_log_extractor = BatteryLoggingExtractor(current_path=cr)
    xiaomi_log = battery_log_extractor.find_xiaomi_log(battery_log_extractor.compress_xiaomi_log(compressed_files))
    checker.check(data=xiaomi_log, typ="Xiaomi log file")

    logger.info("Preparing to search information in log file(s). Please wait...")
    searcher = Searching()
    battery_info = searcher.search_info(xiaomi_log)
    checker.check(data=battery_info, typ="battery information")

    unique_nicknames = {info["nickname"] for info in battery_info}

    logger.info("Preparing to process data. Please wait...")
    data_recorder = Recording(current_path=cr)
    csv_files = data_recorder.create_csv(unique_nicknames)
    checker.check(data=csv_files, typ="csv file")

    processed_csv_files = data_recorder.data_processing(battery_info, csv_files)
    checker.check(data=processed_csv_files, typ="csv file")

    logger.info("Preparing to visualize data. Please wait...")
    visualizer = Visualizing(current_path=cr)
    charts_result = [visualizer.diagrams_generator(filepath=csv_file) for csv_file in csv_files]
    counts = [sum(result) for result in zip(*charts_result)]
    checker.check(data=counts, typ="charts")


if __name__ == "__main__":
    log_filename = "Central.txt"
    log = Log(filename=log_filename)
    current = os.getcwd()
    log.info("Starting running the program now.")
    log.debug("Log module has been initialled successfully.")
    initialize(cr=current, logger=log)

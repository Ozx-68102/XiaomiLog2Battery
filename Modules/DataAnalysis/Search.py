import os
import re
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Manager

from Modules.LogRecord import Log, LogForMultiProc


class Searching:
    def __init__(self) -> None:
        self.logger_filename = "Search.txt"
        self.log = Log(filename=self.logger_filename)

    def _multi_search_info(self, filepath: str, count: Manager) -> dict[str, str] | None:
        def search_capacity(name: str, cont: str, logger: LogForMultiProc) -> float | None:
            try:
                matched_info = re.search(fr"{name}: \s*([\d.]+)\s*mAh", cont)
                return float(matched_info.group(1)) if matched_info else None
            except re.error as sc_e:
                log_error_sc = f"An error occurred while searching for {name}: {str(sc_e)}."
                logger.error(log_error_sc)
                return None

        def fingerprint_recognition(cont: str, logger: LogForMultiProc) -> dict[str, str] | None:
            """
            Extracts multiple key-value pairs from a log file.
            :param cont: The content of the log file as a string.
            :param logger: The logger to use for logging purposes on multiple processes environment.
            :return: **dict[str, str]** - A list of dictionaries, where each dictionary represents a set of extracted
             key-value pairs. If multiple values are associated with a single key, they will be stored as a list within
             the dictionary.
            """
            fingerprint = {}
            try:
                matched_fp_1st = re.search(r"Build fingerprint: '([^']+)'", string=cont).group(1)
                if matched_fp_1st is None:
                    log_error1_fr = f"No fingerprint info found."
                    logger.error(log_error1_fr)
                    return None

                fingerprint["phone_brand"] = matched_fp_1st.split("/", 1)[0]

                log_debug1_fr = f"Recognized the brand of phone: {fingerprint['phone_brand']}."
                logger.debug(log_debug1_fr)

                matched_fp_2nd = re.search(r"([^/]+):\d+/\S+/([^:]+(?:\.[^/]+)+)(?=:)", matched_fp_1st)
                if matched_fp_2nd is None:
                    log_error2_fr = f"No more details in fingerprint of '{fingerprint['phone_brand']}' was found."
                    logger.error(log_error2_fr)
                    return None

                fingerprint["nickname"] = matched_fp_2nd.group(1)

                version = matched_fp_2nd.group(2)
            except re.error as fr_e:
                log_error3_fr = f"An error occurred while searching information: {str(fr_e)}."
                logger.error(log_error3_fr)
                return None

            system_version = f"OS1.{version.split('.', 1)[1]}" if version.startswith("V816") else version
            fingerprint["system_version"] = system_version

            log_debug2_fr = f"Recognized nickname of phone: {fingerprint['nickname']}, system version: {system_version}."
            logger.debug(log_debug2_fr)

            return fingerprint

        def time_processing(disorder_data: str) -> str:
            """
            :param disorder_data: unformatted completely time string
            :return: formatted time string
            """
            time_data = disorder_data.rsplit("-", 3)
            return f"{time_data[0]} {time_data[1]}:{time_data[2]}:{time_data[3]}"

        multi_log = LogForMultiProc(self.logger_filename)

        try:
            filename = os.path.basename(filepath)
            if not filename.startswith("bugreport") and not filename.endswith(".txt"):
                log_warn1 = "No Xiaomi log file found."
                multi_log.warn(log_warn1)
                multi_log.stop()
                return None

            try:
                with open(file=filepath, mode="r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                log_debug1 = f"Log was read successfully. Path: {filepath}."
                multi_log.debug(log_debug1)

            except OSError as e:
                count["failure"] += 1
                total = count["success"] + count["failure"]

                log_error = f"An error occurred while opening a file. Details: {e.strerror}, Path:{filepath}. Count: {total}/{count["total"]}."
                multi_log.error(log_error)
                multi_log.stop()
                return None
            except ValueError as e:
                count["failure"] += 1
                total = count["success"] + count["failure"]

                log_error = f"An ValueError occurred while opening a file. Details: {str(e)}. Count: {total}/{count["total"]}."
                multi_log.error(log_error)
                multi_log.stop()
                return None
            except Exception as e:
                count["failure"] += 1
                total = count["success"] + count["failure"]

                log_error = f"An error occurred while opening a file. Details: {str(e)}. Count: {total}/{count["total"]}."
                multi_log.error(log_error)
                multi_log.stop()
                return None

            keynames = [
                "Estimated battery capacity", "Last learned battery capacity",
                "Min learned battery capacity", "Max learned battery capacity"
            ]

            fgp = ["phone_brand", "nickname", "system_version"]

            log_captured_time = time_processing(filename.split("-", 3)[-1].rsplit(".", 1)[0])

            log_information = {
                "Log Captured Time": str(log_captured_time),
                **{key: search_capacity(key, content, multi_log) for key in keynames}
            }

            fgp_info = fingerprint_recognition(content, multi_log)
            log_information.update({key: fgp_info[key] for key in fgp if fgp_info is not None})

            log_debug2 = f"Xiaomi Log information has caught: {log_information}."
            multi_log.debug(log_debug2)

            count["success"] += 1
            total = count["success"] + count["failure"]

            log_info1 = f"Log information has been matched. Count: {total}/{count["total"]}."
            multi_log.info(log_info1)
        finally:
            multi_log.stop()

        return log_information

    def search_info(self, filepath: str | list[str]) -> list[dict[str, str]] | None:
        if not filepath:
            log_error = "No log file was found."
            self.log.error(log_error)
            return None

        log_files = []

        filepath = [filepath] if isinstance(filepath, str) else filepath
        total_files = len(filepath)
        log_count = Manager().dict({"success": 0, "failure": 0, "total": total_files})

        batch_size = 8
        
        for i in range(0, total_files, batch_size):
            workers = min(total_files, os.cpu_count(), 8)
            batch_files = filepath[i:i + batch_size]

            log_debug = f"{workers} worker(s) started."
            self.log.debug(log_debug)

            with ProcessPoolExecutor(max_workers=workers) as executor:
                futures = [executor.submit(self._multi_search_info, file, log_count) for file in batch_files]

                for future in futures:
                    result = future.result()
                    if result:
                        log_files.append(result)

        def search_battery_capacity_info_display(count: Manager) -> None:
            is_error = False
            match count["success"]:
                case 0:
                    log_text = "Not any information was found"
                    is_error = True
                case _:
                    log_text = f"{count["success"]} information was found successfully"

            match count["failure"]:
                case 0:
                    log_text += "."
                case _:
                    log_text += f", and {count["failure"]} failed."

            if is_error:
                self.log.error(log_text)
            else:
                self.log.info(log_text)

        search_battery_capacity_info_display(log_count)

        return log_files


if __name__ == "__main__":
    pass

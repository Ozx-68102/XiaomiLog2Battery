import os
import re

from Modules.LogManager import Log


class Searching:
    def __init__(self, current_path: str) -> None:
        self.current_path = current_path

        self.log_path = os.path.join(self.current_path, "Log")
        if not os.path.exists(self.log_path):
            os.makedirs(self.log_path)
        self.log = Log(os.path.join(self.log_path, "SearchingLog.txt"))

    def search_info(self, filepath: str) -> None | dict:
        if not filepath.startswith("bugreport") and not filepath.endswith(".txt"):
            log_warn1 = "No log file text from xiaomi was found."
            self.log.warn(log_warn1)
            return None
        try:
            with open(file=filepath, mode="r", encoding="utf-8", errors="ignore") as file:
                content = file.read()

            log_debug1 = f"Log was read successfully. Path:{filepath}"
            self.log.debug(log_debug1)
        except FileNotFoundError as e:
            log_warn2 = f"File not found. Details:{e.strerror}"
            self.log.warn(log_warn2)
        except PermissionError as e:
            log_warn2 = f"Permission denied. Details:{e.strerror}"
            self.log.warn(log_warn2)
        except UnicodeDecodeError as e:
            log_warn2 = f"UnicodeDecodeError. Details:{str(e)}"
            self.log.warn(log_warn2)

        battery_info = {}

        def time_process(ud: str) -> str:
            """
            :param ud: unformatted completely time string
            :return: formatted time string
            """
            te = ud.rsplit("-", 3)
            date = te[0]
            hr = te[1]
            ms = te[2]
            sec = te[3]
            time = f"{hr}:{ms}:{sec}"

            return f"{date} {time}"

        log_time = filepath.split("-", 3)[-1].rsplit(".", 1)[0]
        log_captured_time = time_process(log_time)
        battery_info["Log Captured Time"] = str(log_captured_time)

        match_estimated = re.search(pattern=r"Estimated battery capacity: \s*([\d.]+)\s*mAh", string=content)
        if match_estimated:
            battery_info["Estimated battery capacity"] = float(match_estimated.group(1))

        match_last_learned = re.search(pattern=r"Last learned battery capacity: \s*([\d.]+)\s*mAh", string=content)
        if match_last_learned:
            battery_info["Last learned battery capacity"] = float(match_last_learned.group(1))

        match_min_learned = re.search(pattern=r"Min learned battery capacity: \s*([\d.]+)\s*mAh", string=content)
        if match_min_learned:
            battery_info["Min learned battery capacity"] = float(match_min_learned.group(1))

        match_max_learned = re.search(pattern=r"Max learned battery capacity: \s*([\d.]+)\s*mAh", string=content)
        if match_max_learned:
            battery_info["Max learned battery capacity"] = float(match_max_learned.group(1))

        match_battery_time = re.search(pattern=r"Battery time remaining: \s*([\w\s]+ms)", string=content)
        if match_battery_time:
            battery_info["Battery time remaining"] = match_battery_time.group(1)

        log_debug2 = f"Battery info has caught: {battery_info}"
        self.log.debug(log_debug2)

        return battery_info


if __name__ == "__main__":
    pass

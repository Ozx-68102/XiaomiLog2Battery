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

    def search_info(self, filepath: str | list[str]) -> None | list[dict]:
        def battery_capacity_info(cname: str, s: str) -> float:
            matched_info = re.search(pattern=fr"{cname}: \s*([\d.]+)\s*mAh", string=s)
            if matched_info:
                matched_info = float(matched_info.group(1))

            return matched_info

        def time_process(ud: str) -> str:
            """
            :param ud: unformatted completely time string
            :return: formatted time string
            """
            te = ud.rsplit("-", 3)
            date = te[0]
            time = f"{te[1]}:{te[2]}:{te[3]}"

            return f"{date} {time}"

        filepath = [filepath] if isinstance(filepath, str) else filepath

        battery_infos = []

        for fp in filepath:
            fp = os.path.abspath(fp)
            path = os.path.basename(fp)
            if not path.startswith("bugreport") and not path.endswith(".txt"):
                log_warn1 = "No log file text from xiaomi was found."
                self.log.warn(log_warn1)
                return None

            try:
                with open(file=fp, mode="r", encoding="utf-8", errors="ignore") as file:
                    content = file.read()

                log_debug1 = f"Log was read successfully. Path:{fp}"
                self.log.debug(log_debug1)
            except OSError as e:
                log_error = f"An error occurred while opening a file. Details: {e.strerror} Path:{fp}"
                self.log.error(log_error)
                continue
            except ValueError as e:
                log_error = f"An ValueError occurred while opening a file. Details: {e}"
                self.log.error(log_error)
                continue

            battery_info = {}
            bi_keyname = [
                "Estimated battery capacity", "Last learned battery capacity",
                "Min learned battery capacity", "Max learned battery capacity"
            ]

            log_time = fp.split("-", 3)[-1].rsplit(".", 1)[0]
            log_captured_time = time_process(log_time)

            battery_info["Log Captured Time"] = str(log_captured_time)
            battery_info[bi_keyname[0]] = battery_capacity_info(bi_keyname[0], content)
            battery_info[bi_keyname[1]] = battery_capacity_info(bi_keyname[1], content)
            battery_info[bi_keyname[2]] = battery_capacity_info(bi_keyname[2], content)
            battery_info[bi_keyname[3]] = battery_capacity_info(bi_keyname[3], content)

            match_battery_time = re.search(pattern=r"Battery time remaining: \s*([\w\s]+ms)", string=content)
            if match_battery_time:
                battery_info["Battery time remaining"] = match_battery_time.group(1)

            log_debug2 = f"Battery info has caught: {battery_info}"
            self.log.debug(log_debug2)
            battery_infos.append(battery_info)

        return battery_infos


if __name__ == "__main__":
    pass

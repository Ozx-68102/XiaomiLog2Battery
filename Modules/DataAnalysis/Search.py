import os
import re

from Modules.LogRecord import Log


class Searching:
    def __init__(self, current_path: str) -> None:
        self.current_path = current_path

        self.log_path = os.path.join(self.current_path, "Log")
        if not os.path.exists(self.log_path):
            os.makedirs(self.log_path)
        self.log = Log(os.path.join(self.log_path, "SearchingLog.txt"))

    def search_info(self, filepath: str | list[str]) -> None | list[dict[str, str | float]]:
        def battery_capacity_info(cname: str, s: str) -> float:
            matched_info = re.search(pattern=fr"{cname}: \s*([\d.]+)\s*mAh", string=s)
            if matched_info:
                matched_info = float(matched_info.group(1))

            return matched_info

        def phone_fingerprint_recognition(s: str) -> None | dict[str, str]:
            """
            Extracts multiple key-value pairs from a log file.
            :param s: The content of the log file as a string.
            :return: **dict[str, str]** - A list of dictionaries, where each dictionary represents a set of extracted
             key-value pairs. If multiple values are associated with a single key, they will be stored as a list within
             the dictionary.
            """
            fingerprint = {}

            matched_fp_1st = re.search(pattern=r"Build fingerprint: '([^']+)'", string=s)
            bfing = matched_fp_1st.group(1) if matched_fp_1st else None

            if bfing is None:
                log_error1_pfr = f"No fingerprint info was found."
                self.log.error(log_error1_pfr)
                return None

            log_debug1_pfr = f"Recognized phone fingerprint: {bfing}."
            self.log.debug(log_debug1_pfr)

            matched_fp_2nd = re.search(pattern=r"([^/]+):\d+/\S+/([^:]+(?:\.[^/]+)+)(?=:)", string=bfing)
            if matched_fp_2nd is None:
                log_error1_pfr = f"No details in fingerprint info was found."
                self.log.error(log_error1_pfr)
                return None

            fingerprint["phone_brand"] = bfing.split("/", 1)[0]
            fingerprint["nickname"] = matched_fp_2nd.group(1)

            sys_version = matched_fp_2nd.group(2)
            if (spe_sv := sys_version).startswith("V816"):
                ver_end = spe_sv.split(".", 1)[1]
                sys_version = f"OS1.{ver_end}"

            fingerprint["system_version"] = sys_version

            log_debug2_pfr = (f"Recognized brand: {fingerprint["phone_brand"]}, nickname: {fingerprint["nickname"]},"
                              f" system version: {fingerprint["system_version"]}.")
            self.log.debug(log_debug2_pfr)

            return fingerprint

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

        xmlog_infos = []

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
                log_error = f"An error occurred while opening a file. Details: {e.strerror}, Path:{fp}."
                self.log.error(log_error)
                continue
            except ValueError as e:
                log_error = f"An ValueError occurred while opening a file. Details: {str(e)}."
                self.log.error(log_error)
                continue
            except Exception as e:
                log_error = f"An error occurred while opening a file. Details: {str(e)}."
                self.log.error(log_error)
                continue

            xmlog_info = {}
            cap_keyname = [
                "Estimated battery capacity", "Last learned battery capacity",
                "Min learned battery capacity", "Max learned battery capacity"
            ]

            fgp = ["phone_brand", "nickname", "system_version"]

            log_time = fp.split("-", 3)[-1].rsplit(".", 1)[0]
            log_captured_time = time_process(log_time)

            xmlog_info["Log Captured Time"] = str(log_captured_time)
            xmlog_info[cap_keyname[0]] = battery_capacity_info(cap_keyname[0], content)
            xmlog_info[cap_keyname[1]] = battery_capacity_info(cap_keyname[1], content)
            xmlog_info[cap_keyname[2]] = battery_capacity_info(cap_keyname[2], content)
            xmlog_info[cap_keyname[3]] = battery_capacity_info(cap_keyname[3], content)

            xmlog_info[fgp[0]] = phone_fingerprint_recognition(content)[fgp[0]]
            xmlog_info[fgp[1]] = phone_fingerprint_recognition(content)[fgp[1]]
            xmlog_info[fgp[2]] = phone_fingerprint_recognition(content)[fgp[2]]

            # temporary disabled because it is not belonging to capacity class.
            # match_battery_time = re.search(pattern=r"Battery time remaining: \s*([\w\s]+ms)", string=content)
            # if match_battery_time:
            #     xmlog_info["Battery time remaining"] = match_battery_time.group(1)

            log_debug2 = f"Battery info has caught: {xmlog_info}"
            self.log.debug(log_debug2)
            xmlog_infos.append(xmlog_info)

        return xmlog_infos


if __name__ == "__main__":
    pass

import os
from typing import Literal

from Modules.FileProcess import BatteryLoggingExtractor, FolderOperator
from Modules.DataAnalysis import Recording, Searching, Visualizing
from Modules.LogRecord import Log


def check_error(
        f: list | str | bool | None,
        typ: Literal["compressed file", "Xiaomi log file", "battery information", "csv file", "line chart"]
) -> None:
    def format_str(noun:str, number:int) -> str:
        return noun if (number == 1 or number == 0) else f"{noun}s"

    a = ["compressed file", "Xiaomi log file", "battery information", "csv file", "line chart"]
    try:
        if typ not in a:
            emsg1 = f"'typ' must be one of '{a[0]}', '{a[1]}', '{a[2]}' or {a[3]}, not '{typ}'."
            raise ValueError(emsg1)

        if isinstance(f, str):
            if typ != a[3]:
                emsg2 = f"When the type of 'f' is a string, 'typ' must be '{a[3]}', not '{typ}'."
                raise ValueError(emsg2)
            else:
                if f is None:
                    log_error = f"No {typ} was created."
                    log.error(log_error)
                    exit(1)
                else:
                    log_debug = f"1 {typ} was created."
                    log.debug(log_debug)
        elif isinstance(f, list):
            n = len(f)
            if typ == a[4]:
                count_t = sum(1 for ff in f if ff)
                count_f = len(f) - count_t

                log_info = (f"{count_t} {format_str("file", count_t)} visualized successfully,"
                            f" {count_f} {format_str("file", count_f)} failed.")
                log.info(log_info)
            elif typ == a[3]:
                if n == 0:
                    log_error = f"No {typ} was created."
                    log.error(log_error)
                    exit(1)
                else:
                    log_debug = f"{n} {"csv file was" if n == 1 else "csv files were"} created."
                    log.debug(log_debug)
            else:
                if n > 0:
                    conditions = typ if (typ == a[2]) or (n == 1 and typ != a[2]) else (typ + "s")
                    log_debug = f"Found {n} {conditions}."
                    log.debug(log_debug)
                else:
                    log_error = f"No {typ} was found."
                    log.error(log_error)
                    exit(1)
        elif isinstance(f, bool):
            if typ != a[4]:
                emsg4 = f"When the type of 'f' is a bool, 'typ' must be '{a[4]}', not '{typ}'."
                raise ValueError(emsg4)
            else:
                if not f:
                    emsg5 = "Failed to visualize battery information."
                    raise ValueError(emsg5)
        else:
            emsg6 = f"Variable 'f' must be a list, a string or a bool, not '{f}'."
            raise ValueError(emsg6)
    except ValueError as e:
        log.error(str(e))
        exit(1)


def main(cr):
    fm = FolderOperator(cr)
    zip_filelist = fm.file_recognition(os.path.join(cr, "zips"))
    check_error(zip_filelist, "compressed file")

    ble = BatteryLoggingExtractor(cr)
    p = ble.find_xiaomi_log(ble.compress_xiaomi_log(zip_filelist))
    check_error(p, "Xiaomi log file")

    sear = Searching(cr)
    infos = sear.search_info(p)
    check_error(infos, "battery information")

    pnickname = {info["nickname"] for info in infos}

    rec = Recording(cr)
    check_error(csv_ps := rec.create_csv(pnickname), "csv file")
    check_error(rec.data_processing(infos, csv_ps), "csv file")

    visu = Visualizing(cr)
    count = [visu.pline_chart(csv_p) for csv_p in csv_ps]
    check_error(count, "line chart")


if "__main__" == __name__:
    current = os.getcwd()
    log_path = os.path.join(current, "Log")
    os.makedirs(log_path, exist_ok=True)
    log = Log(os.path.join(log_path, "FinderLog.txt"))
    log.debug("Log module has been initialled successfully.")

    main(current)

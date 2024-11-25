import os
from typing import Literal

from Modules.Compress import Compressing
from Modules.FileManager import FileManager
from Modules.LogManager import Log
from Modules.Record import Recording
from Modules.Search import Searching
from Modules.Visualization import Visualizing


def check_error(
        f: list | str | bool | None,
        typ: Literal["compressed file", "Xiaomi log file", "battery information", "csv file", "line chart"]
) -> None:
    a = ["compressed file", "Xiaomi log file", "battery information", "csv file", "line chart"]
    try:
        if typ not in a:
            emsg1 = f"ValueError: 'typ' must be one of '{a[0]}', '{a[1]}', '{a[2]}' or {a[3]}, not '{typ}'."
            raise ValueError(emsg1)

        if isinstance(f, str):
            if typ != a[3]:
                emsg2 = f"ValueError: When the type of 'f' is a string, 'typ' must be '{a[3]}', not '{typ}'."
                raise ValueError(emsg2)
            else:
                if f is None:
                    log_error = f"No {typ} was created."
                    log.error(log_error)
                    exit(1)
        elif isinstance(f, list):
            if typ == a[3] or typ == a[4]:
                emsg3 = f"ValueError: When the type of 'f' is a list, 'typ' cannot be '{typ}'."
                raise ValueError(emsg3)
            else:
                n = len(f)
                if n > 0:
                    conditions = typ if (typ == a[2]) or (n == 1 and typ != a[2]) else typ + "s"
                    log_debug = f"Found {n} {conditions}."
                    log.debug(log_debug)
                else:
                    log_error = f"No {typ} was found."
                    log.error(log_error)
                    exit(1)
        elif isinstance(f, bool):
            if typ != a[4]:
                emsg4 = f"ValueError: When the type of 'f' is a bool, 'typ' must be '{a[4]}', not '{typ}'."
                raise ValueError(emsg4)
            else:
                if not f:
                    emsg5 = "Failed to visualize battery information."
                    raise ValueError(emsg5)
        else:
            emsg4 = f"ValueError: Variable 'f' must be a list, a string or a bool, not '{f}'."
            raise ValueError(emsg4)
    except ValueError as e:
        log.error(str(e))
        exit(1)


def main(cr):
    fm = FileManager(cr)
    zip_filelist = fm.file_recognition(os.path.join(cr, "zips"))
    check_error(zip_filelist, "compressed file")

    cp = Compressing(cr)
    p = cp.find_xiaomi_log(cp.compress_xiaomi_log(zip_filelist))
    check_error(p, "Xiaomi log file")

    sear = Searching(cr)
    infos = sear.search_info(p)
    check_error(infos, "battery information")

    rec = Recording(cr)
    check_error(csv_p := rec.create_csv(), "csv file")
    check_error(rec.data_processing(infos, csv_p), "csv file")

    visu = Visualizing(cr)
    vpc = visu.pline_chart(csv_p)
    check_error(vpc, "line chart")


current = os.getcwd()
log_path = os.path.join(current, "Log")
if not os.path.exists(log_path):
    os.makedirs(log_path)
log = Log(os.path.join(log_path, "FinderLog.txt"))
log.debug("Log module has been initialled successfully.")

main(current)

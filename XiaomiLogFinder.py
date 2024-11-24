import os
from typing import Literal

from Modules.Compress import Compressing
from Modules.FileManager import FileManager
from Modules.LogManager import Log
from Modules.Record import Recording
from Modules.Search import Searching
from Modules.Visualization import Visualizing


def judge_none(
        f: list | str | None,
        typ: Literal["compressed file", "Xiaomi log file", "battery information", "csv file"]
) -> None:
    try:
        if typ not in (a := ["compressed file", "Xiaomi log file", "battery information", "csv file"]):
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
            if typ == a[3]:
                emsg3 = f"ValueError: When the type of 'f' is a list, 'typ' cannot be '{a[3]}'."
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
        else:
            emsg4 = f"ValueError: Variable 'f' must be a list or a string, not '{f}'."
            raise ValueError(emsg4)
    except ValueError as e:
        log.error(str(e))
        exit(1)


def main(cr):
    fm = FileManager(cr)
    zip_filelist = fm.file_recognition(os.path.join(cr, "zips"))
    judge_none(zip_filelist, "compressed file")

    cp = Compressing(cr)
    p = cp.find_xiaomi_log(cp.compress_xiaomi_log(zip_filelist))
    judge_none(p, "Xiaomi log file")

    sear = Searching(cr)
    infos = sear.search_info(p)
    judge_none(infos, "battery information")

    rec = Recording(cr)
    judge_none(csv_p := rec.create_csv(), "csv file")
    judge_none(rec.data_processing(infos, csv_p), "csv file")

    visu = Visualizing(cr)
    if not visu.pline_chart(csv_p):
        # TODO: merge into the func
        log.error("Failed to visualize battery information.")
        exit(1)


current = os.getcwd()
log_path = os.path.join(current, "Log")
if not os.path.exists(log_path):
    os.makedirs(log_path)
log = Log(os.path.join(log_path, "FinderLog.txt"))
log.debug("Log module has been initialled successfully.")

main(current)

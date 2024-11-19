import os

from Modules.Compress import Compressing
from Modules.FileManager import FileManager
from Modules.LogManager import Log
from Modules.Search import Searching
from Modules.Record import Recording

log_path = os.path.join(os.getcwd(), "Log")
current = os.getcwd()
if not os.path.exists(log_path):
    os.makedirs(log_path)

log = Log(os.path.join(log_path, "FinderLog.txt"))
log.debug("Log module has been initialled successfully.")

fm = FileManager(current)
zip_filelist = fm.file_recognition(os.path.join(current, "zips"))
if zip_filelist is not None:
    log.debug(f"Found {len(zip_filelist)} compressed {"file" if len(zip_filelist) == 1 else "files"}.")
else:
    log.error("No compressed files was found.")
    exit(1)

cp = Compressing(current)
p = cp.find_xiaomi_log(cp.compress_xiaomi_log(zip_filelist))
if p is not None:
    log.debug(f"Found {len(p)} Xiaomi log {"file" if len(p) == 1 else "files"}.")
else:
    log.error("No Xiaomi log file was found.")
    exit(1)

sear = Searching(current)
infos = sear.search_info(p)
if infos is not None:
    log.debug(f"Found {len(infos)} battery information.")
else:
    log.error("No battery information was found.")
    exit(1)

rec = Recording(current)
if (csv_p := rec.create_csv()) is None:
    log.error("No csv file was created.")
    exit(1)

rec.data_processing(infos, csv_p)

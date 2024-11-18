import os

from Modules.Compressing import Compressing
from Modules.LogManager import Log
from Modules.Search import Searching
from Modules.Record import Recording

log_path = os.path.join(os.getcwd(), "Log")
cr = os.getcwd()
if not os.path.exists(log_path):
    os.makedirs(log_path)

log = Log(os.path.join(log_path, "FinderLog.txt"))
log.debug("Log module has been initialled successfully.")


def find_all_zip(current_path):
    exclude_dirs = [".git", ".idea", ".venv", "__pycache__", "Modules", "temp"]
    log_file = []
    for root, dirs, files in os.walk(current_path):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if file.startswith("bugreport") and file.endswith(".zip"):
                log_file.append(os.path.join(root, file))

    return log_file


lf = find_all_zip(cr)
if lf is None:
    log.error("No compressed file was found.")
    exit(1)

if len(lf) == 1:
    log_info1 = "System has detected 1 compressed file."
else:
    log_info1 = f"System has detected {len(lf)} compressed files."

log.info(log_info1)

comp = Compressing(cr)
fp = []
for f in lf:
    flist = comp.compress_xiaomi_log(str(f))
    p = comp.find_xiaomi_log(flist)
    fp.append(p)

if fp is None:
    log.error("No file path was specified.")
    exit(1)

infos = []
sear = Searching(cr)
for sfp in fp:
    ba_info = sear.search_info(sfp)
    infos.append(ba_info)

if infos is None:
    log.error("No battery info was searched.")
    exit(1)

log_info2 = f"System has detected {len(infos)} battery info."
log.info(log_info2)

rec = Recording(cr)
csv_p = rec.create_csv()
if csv_p is None:
    log.error("No csv file was created.")
    exit(1)

rec.data_processing(infos, csv_p)



import os
import shutil
import time
import zipfile
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime
from multiprocessing import Manager
from typing import Literal

from Modules.FileProcess.FolderOperator import FolderOperator
from Modules.LogRecord import Log, LogForMultiProc


class BatteryLoggingExtractor:
    def __init__(self, current_path: str):
        self.current_path = current_path

        self.logger_filename = "BatteryLoggingExtractor.txt"
        self.log = Log(filename=self.logger_filename)

        self.Fop = FolderOperator()
        self.tep = os.path.join(self.current_path, "temp")

    def __manage_temp_dir(self, option: Literal["del", "crt", "reset"], tp: str = None) -> None:
        temp_path = self.tep if (tp is None or tp == self.tep) else os.path.join(self.tep, tp)

        # New syntax for Python 3.10 and above
        match option:
            case "del":
                self.Fop.delete_dir(temp_path)
            case "crt":
                self.Fop.create_dir(temp_path, ignore_tips=True)
            case "reset":
                self.Fop.delete_dir(temp_path)
                self.Fop.create_dir(temp_path, ignore_tips=True)
            case _:
                errmsg = f"'option' variable was expected to receive 'del', 'crt' or 'reset', not '{option}'."
                raise ValueError(errmsg)


    def __movefile(self, sp: str, dp: str, count: int, total: int) -> bool:
        try:
            os.remove(dp)
            shutil.move(src=sp, dst=dp)
            log_info = f"Successfully overwritten Xiaomi Log. Name:{os.path.basename(dp)}. Count:{count}/{total}."
            self.log.info(log_info)
            return True
        except OSError as e:
            log_error = f"An error occurred while overwriting Xiaomi Log. Details: {e.strerror} Count:{count}/{total}."
            self.log.error(log_error)

        return False

    def _multi_compress_func(self, filepath: str, count: Manager) -> list[str] | None:
        logger = LogForMultiProc(self.logger_filename)
        try:
            step = 1
            if not filepath.startswith("bugreport") and not filepath.endswith(".zip"):
                count["failure"] += 1
                total = count["success"] + count["failure"]

                log_warn1_mcf = f"No compress file found in '{filepath}'. Count:{total}/{count["total"]}."
                logger.warn(log_warn1_mcf)
                logger.stop()
                return None

            name = os.path.basename(filepath).split(".", 1)[0]
            temp = os.path.join(self.tep, f"temp_{name}")

            self.__manage_temp_dir(option="del", tp=temp)

            current_file = filepath

            while current_file:
                log_debug1_mcf = f"Starting decompression process {step} for {current_file}."
                logger.debug(log_debug1_mcf)
                self.__manage_temp_dir(option="crt", tp=temp)

                try:
                    with zipfile.ZipFile(file=current_file, mode="r") as zip_ref:
                        zip_ref.extractall(temp)
                        file_list = zip_ref.namelist()

                except zipfile.BadZipFile as e:
                    count["failure"] += 1
                    total = count["success"] + count["failure"]
                    log_warn_mcf = (f"Decompression process failed for '{current_file}' on process {step}, "
                                    f"maybe this compressed file is corrupted. Details: {str(e)}. "
                                    f"Count: {total}/{count["total"]}.")
                    logger.warn(log_warn_mcf)
                    logger.stop()
                    return None

                nested_zip = None
                for file in file_list:
                    if file.startswith("bugreport") and file.endswith(".zip"):
                        nested_zip = os.path.join(temp, file)
                        break

                if nested_zip:
                    log_debug2_mcf = f"Decompression process {step}: Nested zip file {nested_zip} found."
                    logger.debug(log_debug2_mcf)
                    current_file = nested_zip
                    step += 1
                else:
                    count["success"] += 1
                    total = count["success"] + count["failure"]
                    log_info_mcf = f"Decompression finished. Count:{total}/{count["total"]}."
                    logger.info(log_info_mcf)

                    log_debug3_mcf = (f"Decompression process {step}: No nested zip file found."
                                      f"Process completed for {current_file}.")
                    logger.debug(log_debug3_mcf)

                    current_file = None
        finally:
            logger.stop()

        return [os.path.join(temp, file) for file in file_list]


    def compress_xiaomi_log(self, filepath: str | list[str]) -> list[str] | None:
        if not filepath:
            log_error = "No log file was found."
            self.log.error(log_error)
            return None

        self.__manage_temp_dir(option="reset", tp=self.tep)

        processed_files = []

        filepath = [filepath] if isinstance(filepath, str) else filepath
        total_files = len(filepath)
        zipfile_count = Manager().dict({"success": 0, "failure": 0, "total": total_files})

        # "psutil" library cannot be use because it will cause some troublesome problems that may not have suitable solution currently
        if total_files < os.cpu_count():
            workers = total_files
        else:
            workers = os.cpu_count()

        log_debug = f"{workers} worker(s) started."
        self.log.debug(log_debug)

        with ProcessPoolExecutor(workers) as executor:
            futures = [executor.submit(self._multi_compress_func, file, zipfile_count) for file in filepath]

            for future in futures:
                result = future.result()
                if result:
                    processed_files.extend(result)

        def compress_info_display(count: Manager) -> None:
            is_error = False
            match count["success"]:
                case 0:
                    log_text = "Not any Xiaomi log files was decompressed successfully"
                    is_error = True
                case 1:
                    log_text = f"1 Xiaomi log file was decompressed successfully"
                case _:
                    log_text = f"{count['success']} Xiaomi log files were decompressed successfully"

            match count["failure"]:
                case 0:
                    log_text += "."
                case _:
                    log_text += f", and {count["failure"]} failed."

            if is_error:
                self.log.error(log_text)
            else:
                self.log.info(log_text)


        compress_info_display(zipfile_count)

        return processed_files

    def find_xiaomi_log(self, filelist: list[str], batch: bool = True) -> list[str] | None:
        """
        Find log files from xiaomi log files which are decompressed. Solely process or Batch process are all supported.
        :param filelist: a list of log files (temp)
        :param batch: If it is "True", it provides a function of batch processing.
        :return: Success => list[str], Failure => None
        """
        files_path = os.path.join(self.current_path, "files")
        self.Fop.create_dir(files_path, ignore_tips=True)

        to_overwrite_files = []
        founded_files = []
        ans = None

        # Try to process each file
        for file in filelist:
            filename = os.path.basename(file)
            if filename.startswith("bugreport") and filename.endswith(".txt"):
                dst_path = os.path.join(files_path, filename)
                src_path = file

                # if file has been existed, add it to the list
                if os.path.exists(dst_path):
                    to_overwrite_files.append((dst_path, src_path))
                else:
                    # otherwise move it directly
                    try:
                        shutil.move(src=src_path, dst=dst_path)
                        log_info1 = f"Successfully found Xiaomi Log. Name: {os.path.basename(file)}"
                        self.log.info(log_info1)
                        founded_files.append(dst_path)
                    except FileNotFoundError as e:
                        log_error1 = f"File not found: {e.strerror}."
                        self.log.error(log_error1)
                        self.__manage_temp_dir(option="del")
                        return None
                    except (shutil.Error, OSError) as e:
                        log_error1 = f"An error occurred while finding Xiaomi Log: {e.strerror}."
                        self.log.error(log_error1)
                        self.__manage_temp_dir(option="del")
                        return None
                    except Exception as e:
                        log_error1 = f"An error occurred while finding Xiaomi Log: {str(e)}."
                        self.log.error(log_error1)
                        self.__manage_temp_dir(option="del")
                        return None

        # if there are files with same name, ask user whether process it batch
        if to_overwrite_files:
            num = len(to_overwrite_files)

            if batch:
                log_info2 = f"{num} file(s) found with the same name."
                self.log.info(log_info2)
                time.sleep(0.07)

                while ans not in ["y", "n"]:
                    ans = input("Do you want to overwrite it all ([y]/n):").lower()
                    ans = "y" if len(ans) == 0 else ans
                    log_debug1 = f"User input : {ans}"
                    self.log.debug(log_debug1)
                    if ans == "y":
                        filecount = 1
                        for dst_path, src_path in to_overwrite_files:
                            if self.__movefile(sp=src_path, dp=dst_path, count=filecount, total=num):
                                founded_files.append(dst_path)

                            filecount = filecount + 1 if filecount < num else num

                    elif ans == "n":
                        log_info3 = f"{num} old files has been retained."
                        self.log.info(log_info3)
                        founded_files.extend(dst_path for dst_path, src_path in to_overwrite_files)
                    else:
                        log_warn1 = "Invalid input. Please try again."
                        self.log.warn(log_warn1)
            else:
                filecount = 1
                grammar_suit = "file" if num == 1 else "files"
                log_info2 = f"System has found {num} {grammar_suit} with the same name."
                self.log.info(log_info2)

                log_info3 = "Now you can make decisions to retain the file or replace it."
                self.log.info(log_info3)

                for dst_path, src_path in to_overwrite_files:
                    dst_mtime = time.localtime(os.path.getmtime(dst_path))
                    dst_mtime = datetime.fromtimestamp(time.mktime(dst_mtime))
                    dst_mtime = dst_mtime.strftime("%Y-%m-%d %H:%M:%S")

                    src_mtime = time.localtime(os.path.getmtime(src_path))
                    src_mtime = datetime.fromtimestamp(time.mktime(src_mtime))
                    src_mtime = src_mtime.strftime("%Y-%m-%d %H:%M:%S")

                    log_info4 = f"[{filecount}]Old file modified date: {dst_mtime}"
                    self.log.info(log_info4)

                    log_info5 = f"[{filecount}]New file modified date: {src_mtime}"
                    self.log.info(log_info5)

                    while ans not in ["y", "n"]:
                        log_debug1 = f"[{filecount}]Do you want to overwrite it ([y]/n):"
                        self.log.debug(log_debug1)

                        ans = input(log_debug1).lower()
                        ans = "y" if len(ans) == 0 else ans
                        log_debug2 = f"User input : {ans}"
                        self.log.debug(log_debug2)

                        if ans == "y":
                            if self.__movefile(sp=src_path, dp=dst_path, count=filecount, total=num):
                                founded_files.append(dst_path)

                            filecount = filecount + 1 if filecount < num else num
                            break
                        elif ans == "n":
                            log_info3 = f"{num} old file(s) has been retained."
                            self.log.info(log_info3)
                        else:
                            log_error = "Invalid input. Please try again."
                            self.log.error(log_error)

        self.__manage_temp_dir(option="del")

        if len(founded_files) > 0:
            log_info6 = f"Found {len(founded_files)} Xiaomi Log file(s)."
            self.log.info(log_info6)
        else:
            log_error = "Failed to find any Xiaomi Log file(s)."
            self.log.error(log_error)

        return founded_files


if __name__ == "__main__":
    pass

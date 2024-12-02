import datetime
import os
import shutil
import time
import zipfile

from Modules.FileProcess.FolderOperator import FolderOperator
from Modules.LogRecord import Log


class Compressing:
    def __init__(self, current_path: str) -> None:
        self.current_path = current_path
        self.log_path = os.path.join(self.current_path, "Log")
        if not os.path.exists(self.log_path):
            os.makedirs(self.log_path)
        self.log = Log(os.path.join(self.log_path, "CompressingLog.txt"))
        self.fm = FolderOperator(self.current_path)
        self.basic_temp_path = os.path.join(self.current_path, "temp")

    def __create_temp_dir(self, temp_path: str = None) -> None:
        temp_path = os.path.join(self.basic_temp_path, temp_path) if temp_path is not None else self.basic_temp_path
        self.fm.create_dir(temp_path, ignore_tips=True)

    def __del_temp_dir(self, temp_path: str = None) -> None:
        temp_path = os.path.join(self.basic_temp_path, temp_path) if temp_path is not None else self.basic_temp_path
        self.fm.delete_dir(temp_path)

    def __movefile(self, sp: str, dp: str, count: int) -> bool:
        try:
            os.remove(dp)
            shutil.move(src=sp, dst=dp)
            log_info = f"[{count}] Successfully overwritten Xiaomi Log. Name:{os.path.basename(dp)}."
            self.log.info(log_info)
            return True
        except OSError as e:
            log_error = f"[{count}]An error occurred while overwriting Xiaomi Log. Details: {e.strerror}"
            self.log.error(log_error)

        return False

    def compress_xiaomi_log(self, filepath: str | list[str]) -> list[str] | None:
        if not filepath:
            log_warn1 = "No log file was found."
            self.log.warn(log_warn1)
            return None

        zipfile_count = 0

        if os.path.exists(self.basic_temp_path):
            self.__del_temp_dir()

        self.__create_temp_dir()

        if isinstance(filepath, str):
            filepath = [filepath]

        processed_files = []

        for fp in filepath:
            step = 1
            if not fp.startswith("bugreport") and not fp.endswith(".zip"):
                log_warn1 = f"No log file from Xiaomi was found. Path:{fp}."
                self.log.warn(log_warn1)
                continue

            name = os.path.basename(fp).split(".", 1)[0]

            # Create a directory in temp dir
            temp = os.path.join(self.basic_temp_path, f"temp-{name}")
            if os.path.exists(temp):
                self.__del_temp_dir()

            current_file = fp

            while current_file:
                # continue to decompress until there is no zip file
                log_debug1 = f"Starting decompression process {step} for {current_file}..."
                self.log.debug(log_debug1)
                self.__create_temp_dir(temp)

                try:
                    with zipfile.ZipFile(current_file, "r") as zip_ref:
                        zip_ref.extractall(temp)
                        file_list = zip_ref.namelist()
                except zipfile.BadZipfile as e:
                    log_error = (f"[{zipfile_count}]Decompression process {step}:"
                                 f" Bad compressed file error: {e.strerror}")
                    self.log.error(log_error)
                    self.__del_temp_dir(temp)
                    continue

                nested_zip = None
                for file in file_list:
                    if file.startswith("bugreport") and file.endswith(".zip"):
                        nested_zip = os.path.join(temp, file)
                        break

                if nested_zip:
                    log_debug2 = f"Decompression process {step}: Nested zip file {nested_zip} found."
                    self.log.debug(log_debug2)
                    current_file = nested_zip
                    step += 1
                else:
                    zipfile_count = zipfile_count + 1 if zipfile_count < len(filepath) else zipfile_count
                    log_info = f"File {zipfile_count} decompression finished."
                    self.log.info(log_info)

                    log_debug2 = (f"Decompression process {step}: No nested zip files found."
                                  f" Process complete for {current_file}.")
                    self.log.debug(log_debug2)

                    # Decompression completed
                    current_file = None

            # At the end of the recursion, add final files into the list
            # Ensure this only happens after the second decompression is finished
            processed_files.extend([os.path.join(temp, file) for file in file_list])

        log_info2 = f"Successfully compressed {len(filepath)} Xiaomi Log {"file" if len(filepath) == 1 else "files"}."
        self.log.info(log_info2)
        return processed_files

    def find_xiaomi_log(self, filelist: list[str], batch: bool = True) -> list[str] | None:
        """
        Find log files from xiaomi log files which are decompressed. Solely process or Batch process are all supported.
        :param filelist: a list of log files (temp)
        :param batch: If it is "True", it provides a function of batch processing.
        :return: Success => list[str], Failure => None
        """
        files_path = os.path.join(self.current_path, "files")
        self.fm.create_dir(files_path, ignore_tips=True)

        to_overwrite_files = []
        processed_files = []
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
                        processed_files.append(dst_path)
                    except FileNotFoundError as e:
                        log_error1 = f"File not found: {e.strerror}."
                        self.log.error(log_error1)
                        self.__del_temp_dir()
                        return None
                    except (shutil.Error, OSError) as e:
                        log_error1 = f"An error occurred while finding Xiaomi Log: {e.strerror}."
                        self.log.error(log_error1)
                        self.__del_temp_dir()
                        return None
                    except Exception as e:
                        log_error1 = f"An error occurred while finding Xiaomi Log: {str(e)}."
                        self.log.error(log_error1)
                        self.__del_temp_dir()
                        return None

        # if there are files with same name, ask user whether process it batch
        if to_overwrite_files:
            num = len(to_overwrite_files)

            if batch:
                log_info2 = f"{num} {"file was" if num == 1 else "files were"} found with the same name."
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
                            if self.__movefile(sp=src_path, dp=dst_path, count=filecount):
                                processed_files.append(dst_path)

                            filecount = filecount + 1 if filecount < num else num

                    elif ans == "n":
                        log_info3 = f"{num} old files has been retained."
                        self.log.info(log_info3)
                        processed_files.extend(dst_path for dst_path, src_path in to_overwrite_files)
                    else:
                        log_warn1 = "Invalid input. Please try again."
                        self.log.warn(log_warn1)
            else:
                filecount = 1
                log_info2 = f"System has found {num} {"file" if num == 1 else "files"} with the same name."
                self.log.info(log_info2)

                log_info3 = "Now you can make decisions to retain the file or replace it."
                self.log.info(log_info3)

                for dst_path, src_path in to_overwrite_files:
                    dst_mtime = time.localtime(os.path.getmtime(dst_path))
                    dst_mtime = datetime.datetime.fromtimestamp(time.mktime(dst_mtime))
                    dst_mtime = dst_mtime.strftime("%Y-%m-%d %H:%M:%S")

                    src_mtime = time.localtime(os.path.getmtime(src_path))
                    src_mtime = datetime.datetime.fromtimestamp(time.mktime(src_mtime))
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
                            if self.__movefile(sp=src_path, dp=dst_path, count=filecount):
                                processed_files.append(dst_path)

                            filecount = filecount + 1 if filecount < num else num
                            break

        self.__del_temp_dir()
        return processed_files


if __name__ == "__main__":
    pass

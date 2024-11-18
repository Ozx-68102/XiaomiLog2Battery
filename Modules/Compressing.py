import datetime
import os
import shutil
import time
import zipfile

from Modules.FileManager import FileManager
from Modules.LogManager import Log


class Compressing:
    def __init__(self, current_path: str) -> None:
        self.current_path = current_path
        self.log_path = os.path.join(self.current_path, "Log")
        if not os.path.exists(self.log_path):
            os.makedirs(self.log_path)
        self.log = Log(os.path.join(self.log_path, "CompressingLog.txt"))
        self.fm = FileManager(self.current_path)
        self.temp_path = os.path.join(self.current_path, "temp")

    def __create_temp_dir(self) -> None:
        self.fm.create_dir(self.temp_path, ignore_tips=True)

    def __del_temp_dir(self) -> None:
        self.fm.delete_dir(self.temp_path)

    def compress_xiaomi_log(self, filepath: str) -> list[str] | None:
        if not filepath.startswith("bugreport") and not filepath.endswith(".zip"):
            log_warn1 = "No log file from xiaomi was found."
            self.log.warn(log_warn1)
            return None

        step = 1

        if os.path.exists(self.temp_path):
            self.__del_temp_dir()
            exit(0)

        self.__create_temp_dir()

        try:
            current_file = filepath

            while True:
                log_debug1 = f"Starting decompression process {step}..."
                self.log.debug(log_debug1)

                with zipfile.ZipFile(current_file, "r") as zip_ref:
                    zip_ref.extractall(self.temp_path)
                    file_list = zip_ref.namelist()

                nested_zip = None
                for file in file_list:
                    if file.startswith("bugreport") and file.endswith(".zip"):
                        nested_zip = os.path.join(self.temp_path, file)
                        break

                if nested_zip is not None:
                    log_debug2 = f"Decompression process {step}: Nested zip file {nested_zip} was found."
                    self.log.debug(log_debug2)
                    current_file = nested_zip
                    step += 1
                else:
                    log_debug2 = (f"Decompression process {step}: No any nested zip file was found."
                                  f" Decompression process will be broken soon.")
                    self.log.debug(log_debug2)
                    return file_list

        except zipfile.BadZipfile as e:
            log_warn2 = f"Decompression process {step}: Bad compressed file error: {e.strerror}"
            self.log.warn(log_warn2)
            self.__del_temp_dir()
            return None

    def find_xiaomi_log(self, filelist: list[str]) -> str | None:
        files_path = os.path.join(self.current_path, "files")
        self.fm.create_dir(files_path, ignore_tips=True)

        for file in filelist:
            if file.startswith("bugreport") and file.endswith(".txt"):
                dst_path = os.path.join(files_path, file)
                src_path = os.path.join(self.temp_path, file)

                if os.path.exists(dst_path):
                    dst_mtime = time.localtime(os.path.getmtime(dst_path))
                    dst_mtime = datetime.datetime.fromtimestamp(time.mktime(dst_mtime))
                    dst_mtime = dst_mtime.strftime("%Y-%m-%d %H:%M:%S")

                    src_mtime = time.localtime(os.path.getmtime(src_path))
                    src_mtime = datetime.datetime.fromtimestamp(time.mktime(src_mtime))
                    src_mtime = src_mtime.strftime("%Y-%m-%d %H:%M:%S")

                    log_info1 = "System has found the file with the same name."
                    self.log.info(log_info1)

                    log_info2 = f"Old file modified date: {dst_mtime}"
                    self.log.info(log_info2)

                    log_info3 = f"New file modified date: {src_mtime}"
                    self.log.info(log_info3)
                    time.sleep(0.007)

                    while True:
                        log_debug1 = "Do you want to overwrite it ([y]/n): "
                        self.log.debug(log_debug1)
                        ans = input(log_debug1).lower()
                        if ans == "":
                            ans = "y"
                        self.log.debug(f"User input : {ans}")

                        if ans == "y":
                            try:
                                os.remove(path=dst_path)
                                shutil.move(src=src_path, dst=dst_path)
                                time.sleep(0.007)

                                log_info4 = f"Successfully found Xiaomi Log. Name: {file}"
                                self.log.info(log_info4)
                                self.__del_temp_dir()
                                return dst_path

                            except shutil.Error as e:
                                log_error1 = f"An error occurred: {e.strerror}"
                                self.log.error(log_error1)
                                self.__del_temp_dir()
                                return None
                            except os.error as e:
                                log_error2 = f"An error occurred: {e.strerror}"
                                self.log.error(log_error2)
                                self.__del_temp_dir()
                                return None
                        elif ans == "n":
                            log_info = "Old file has been retained."
                            self.log.info(log_info)
                            self.__del_temp_dir()
                            return dst_path
                        else:
                            log_warn = "Invalid input. Please try again."
                            self.log.warn(log_warn)
                            self.__del_temp_dir()
                            continue
                else:
                    try:
                        shutil.move(src=src_path, dst=dst_path)
                        self.__del_temp_dir()
                        log_info4 = f"Successfully found Xiaomi Log. Name: {file}"
                        self.log.info(log_info4)
                        return dst_path
                    except shutil.Error as e:
                        log_error1 = f"An error occurred: {e.strerror}"
                        self.log.error(log_error1)
                        self.__del_temp_dir()
                        return None


if __name__ == "__main__":
    comp = Compressing(os.getcwd())
    a = comp.compress_xiaomi_log(r"../bugreport-2024-10-09-120741.zip")
    b = comp.find_xiaomi_log(a)
    print(b)

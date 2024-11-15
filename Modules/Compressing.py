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

    def compress_xiaomi_log(self, filepath) -> list[str] | None:
        if not filepath.startswith("bugreport") and not filepath.endswith(".zip"):
            log_warn1 = "No log file from xiaomi was found."
            self.log.warn(log_warn1)
            return None

        step = 1
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
            log_warn2 = f"Decompression process {step}: Bad zip file error: {e.strerror}"
            self.log.warn(log_warn2)
            self.__del_temp_dir()
            return None

    def find_xiaomi_log(self, filelist: list) -> None:
        files_path = os.path.join(self.current_path, "files")
        self.fm.create_dir(files_path, ignore_tips=True)

        for file in filelist:
            if file.startswith("bugreport") and file.endswith(".txt"):
                dst_path = os.path.join(files_path, file)
                src_path = os.path.join(self.temp_path, file)

                if os.path.exists(dst_path):
                    dst_mtime = time.localtime(os.path.getmtime(dst_path)).strftime("%Y-%m-%d %H:%M:%S")
                    src_mtime = time.localtime(os.path.getmtime(src_path)).strftime("%Y-%m-%d %H:%M:%S")

                    log_info1 = "System has found the file with the same name."
                    self.log.info(log_info1)
                    print(log_info1)

                    log_info2 = f"Old file modified date: {dst_mtime}"
                    self.log.info(log_info2)
                    print(log_info2)

                    log_info3 = f"New file modified date: {src_mtime}"
                    self.log.info(log_info3)
                    print(log_info3)

                    while True:
                        log_debug1 = "Do you want to overwrite it ([y]/n): "
                        self.log.debug(log_debug1)
                        ans1 = input(log_debug1).lower()
                        self.log.debug(f"User input : {ans1}")

                        if ans1 == "y" or ans1 == "":
                            log_debug2 = "Confirm again ([y]/n): "
                            self.log.debug(log_debug2)
                            ans2 = input(log_debug2).lower()
                            self.log.debug(f"User input : {ans2}")

                            if ans2 == "y" or ans2 == "":
                                try:
                                    os.remove(path=dst_path)
                                    shutil.move(src=src_path, dst=dst_path)
                                except shutil.Error as e:
                                    log_error1 = f"An error occurred: {e.strerror}"
                                    self.log.error(log_error1)
                                except os.error as e:
                                    log_error2 = f"An error occurred: {e.strerror}"
                                    self.log.error(log_error2)

                                self.__del_temp_dir()
                                break
                            elif ans2 == "n":
                                log_info = "Old file has been retained."
                                self.log.info(log_info)
                                print(log_info)
                                continue
                            else:
                                log_warn = "Invalid input. Please try again."
                                self.log.warn(log_warn)
                                continue
                        elif ans1 == "n":
                            log_info = "Old file has been retained."
                            self.log.info(log_info)
                            print(log_info)
                            continue
                        else:
                            log_warn = "Invalid input. Please try again."
                            self.log.warn(log_warn)
                            continue
                else:
                    try:
                        shutil.move(src=src_path, dst=dst_path)
                    except shutil.Error as e:
                        log_error1 = f"An error occurred: {e.strerror}"
                        self.log.error(log_error1)

                    self.__del_temp_dir()
                    log_info4 = f"Successfully found Xiaomi Log. Name: {file}"
                    self.log.info(log_info4)
                    print(log_info4)


if __name__ == "__main__":
    comp = Compressing(os.getcwd())
    a = comp.compress_xiaomi_log(r"../bugreport-2024-10-09-120741.zip")
    comp.find_xiaomi_log(a)

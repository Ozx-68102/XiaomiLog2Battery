import os
import shutil

from Modules.LogManager import Log


class FileManager:
    def __init__(self, current_path: str):
        self.path = None
        self.current_path = current_path
        self.log_path = os.path.join(self.current_path, "Log")
        if not os.path.exists(self.log_path):
            os.makedirs(self.log_path)
        self.log = Log(path=os.path.join(self.log_path, "FileManagerLog.txt"))

    def __empty_path(self) -> ValueError | None:
        if str.isspace(self.path):
            errmsg = "No specified file path."
            raise ValueError(errmsg)
        else:
            return None

    def create_dir(self, path: str | None = None, ignore_tips: bool = False) -> None:
        self.path = path
        self.__empty_path()

        self.log.debug(f"The argument of parameter 'ignore_tips' is {ignore_tips}.")

        if os.path.exists(self.path):
            if not ignore_tips:
                log_info1 = ("Directory has already existed. If you want to overwrite it,"
                             " all the files under it will be deleted.")
                self.log.info(log_info1)
                print(log_info1)

                while True:
                    log_debug1 = "Do you want to overwrite it ([y]/n)?"
                    self.log.debug(log_debug1)
                    ans1 = input(log_debug1).lower()
                    if len(ans1) == 0:
                        ans1 = "y"
                    self.log.info(f"User input: {ans1}")

                    if ans1 == "y":
                        log_debug2 = "Confirm again ([y]/n):"
                        self.log.debug(log_debug2)
                        ans2 = input(log_debug2).lower()
                        if len(ans2) == 0:
                            ans2 = "y"
                        self.log.info(f"User input: {ans2}")

                        if ans2 == "y":
                            shutil.rmtree(self.path)
                            os.makedirs(self.path)
                            break

                        elif ans2 == "n":
                            log_info2 = "Directory will not be overwritten."
                            self.log.info(log_info2)
                            print(log_info2)
                            continue
                        else:
                            log_warn = "Invalid input. Please try again."
                            self.log.warn(log_warn)
                            continue
                    elif ans1 == "n":
                        log_info3 = "Directory will not be overwritten."
                        self.log.info(log_info3)
                        print(log_info3)
                        continue
                    else:
                        log_warn = "Invalid input. Please try again."
                        self.log.warn(log_warn)
                        continue

                log_info4 = "Directory overwrote successfully."
                self.log.info(log_info4)
                print(log_info4)
            else:
                try:
                    os.makedirs(self.path, exist_ok=True)
                    self.log.info("Directory created successfully.")
                except OSError as e:
                    self.log.warn(e.strerror)
        else:
            os.makedirs(self.path)
            self.log.info("Directory created successfully.")

    def delete_dir(self, path: str = None, __called_by_cmd: bool = True) -> True | False:
        self.log.debug(f"The argument of parameter '__called_by_cmd' is {__called_by_cmd}.")
        self.path = path
        self.__empty_path()

        if not os.path.exists(self.path):
            if not __called_by_cmd:
                self.log.error("Directory does not exist.")

            return False

        try:
            shutil.rmtree(self.path)
        except FileNotFoundError:
            self.log.warn(f"No such directory: {self.path}.")

        if not __called_by_cmd:
            log_info = "Directory deleted successfully."
            self.log.info(log_info)
            print(log_info)

        return True


if __name__ == "__main__":
    file_manager = FileManager(os.getcwd())
    file_manager.create_dir(path=r"../tmp")
    file_manager.delete_dir(path=r"../tmp")

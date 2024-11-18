import os
import shutil

from Modules.LogManager import Log


class FileManager:
    def __init__(self, current_path: str) -> None:
        self.path = None
        self.current_path = current_path
        self.log_path = os.path.join(self.current_path, "Log")
        if not os.path.exists(self.log_path):
            os.makedirs(self.log_path)
        self.log = Log(path=os.path.join(self.log_path, "FileManagerLog.txt"))

    def __empty_path(self) -> ValueError | None:
        if self.path is None or str.isspace(self.path):
            errmsg = "No specified file path."
            raise ValueError(errmsg)
        else:
            return None

    def create_dir(self, path: str, ignore_tips: bool = False) -> str | None:
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
                    ans = input(log_debug1).lower()
                    if len(ans) == 0:
                        ans = "y"
                    self.log.info(f"User input: {ans}")

                    if ans == "y":
                        try:
                            shutil.rmtree(self.path)
                            os.makedirs(self.path)
                            
                            log_info4 = "Directory overwrote successfully."
                            self.log.info(log_info4)
                            
                            return self.path
                        except shutil.Error as e:
                            log_error1 = f"An error occurred: {e.strerror}"
                            self.log.error(log_error1)
                            return None
                        except os.error as e:
                            log_error2 = f"An error occurred: {e.strerror}"
                            self.log.error(log_error2)
                            return None
                    elif ans == "n":
                        log_info3 = "Directory has been retained."
                        self.log.info(log_info3)
                        return self.path
                    else:
                        log_warn = "Invalid input. Please try again."
                        self.log.warn(log_warn)
                        continue
            else:
                try:
                    os.makedirs(self.path, exist_ok=True)
                    return self.path
                except OSError as e:
                    self.log.warn(e.strerror)
                    return None
        else:
            os.makedirs(self.path)
            self.log.debug("Directory created successfully.")
            return self.path

    def delete_dir(self, path: str, called_by_cmd: bool = True) -> True | False:
        self.log.debug(f"The argument of parameter 'called_by_cmd' is {called_by_cmd}.")
        self.path = path
        self.__empty_path()

        if not os.path.exists(self.path):
            if not called_by_cmd:
                self.log.error("Directory does not exist.")

            return False

        try:
            shutil.rmtree(self.path)
        except FileNotFoundError:
            self.log.warn(f"No such directory: {self.path}.")
        except OSError as e:
            self.log.warn(f"OSError: {e.strerror}.")

        if not called_by_cmd:
            log_info = "Directory deleted successfully."
            self.log.info(log_info)
        else:
            log_debug = "Directory deleted successfully."
            self.log.debug(log_debug)

        return True


if __name__ == "__main__":
    file_manager = FileManager(os.getcwd())
    file_manager.create_dir(path=r"../temp")
    file_manager.delete_dir(path=r"../temp")

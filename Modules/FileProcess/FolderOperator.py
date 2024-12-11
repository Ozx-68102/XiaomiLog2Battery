import os
import shutil

from Modules.LogRecord import Log


class FolderOperator:
    def __init__(self, current_path: str) -> None:
        self.path = None
        self.current_path = current_path
        self.log_path = os.path.join(self.current_path, "Log")
        if not os.path.exists(self.log_path):
            os.makedirs(self.log_path)
        self.log = Log(path=os.path.join(self.log_path, "FolderOperator.txt"))

    def __empty_path(self) -> ValueError | None:
        if self.path is None or str.isspace(self.path):
            errmsg = "No specified file path."
            raise ValueError(errmsg)
        else:
            return None

    def create_dir(self, path: str, ignore_tips: bool = False) -> str | None:
        self.path = path
        self.__empty_path()

        self.log.debug(f"ignore_tips={ignore_tips}.")

        if os.path.exists(self.path):
            if not ignore_tips:
                log_info1 = ("Directory has already existed. If you want to overwrite it,"
                             " all the files under it will be deleted.")
                self.log.info(log_info1)

                ans = None

                while ans not in ["y", "n"]:
                    log_debug1 = "Do you want to overwrite it ([y]/n)?"
                    self.log.debug(log_debug1)
                    ans = input(log_debug1).lower()
                    ans = "y" if len(ans) == 0 else ans
                    self.log.info(f"User input: {ans}")

                    if ans == "y":
                        try:
                            shutil.rmtree(self.path)
                            os.makedirs(self.path)
                            
                            log_info4 = "Directory overwrote successfully."
                            self.log.info(log_info4)
                            
                            return self.path
                        except PermissionError as e:
                            log_error = f"Permission error while overwriting the directory: {e.strerror}."
                            self.log.error(log_error)
                            return None
                        except FileNotFoundError as e:
                            log_error = f"File not found while overwriting the directory: {e.strerror}."
                            self.log.error(log_error)
                            return None
                        except (shutil.Error, OSError) as e:
                            log_error = f"An error occurred while overwriting the directory: {e.strerror}."
                            self.log.error(log_error)
                            return None
                        except Exception as e:
                            log_error = f"An error occurred while overwriting the directory: {str(e)}."
                            self.log.error(log_error)
                            return None
                    elif ans == "n":
                        log_info3 = "Directory has been retained."
                        self.log.info(log_info3)
                        return self.path
                    else:
                        log_warn = "Invalid input. Please try again."
                        self.log.warn(log_warn)
            else:
                try:
                    os.makedirs(self.path, exist_ok=True)
                    return self.path
                except OSError as e:
                    log_error = f"An error occurred while creating the directory: {e.strerror}."
                    self.log.error(log_error)
                    return None
                except Exception as e:
                    log_error = f"An error occurred while creating the directory: {str(e)}."
                    self.log.error(log_error)
                    return None
        else:
            os.makedirs(self.path)
            log_debug = "Directory created successfully."
            self.log.debug(log_debug)
            return self.path

    def file_recognition(
            self,
            path: str,
            exclude_dir: list[str] | tuple[str] = (".git", ".idea", ".venv", "__pycache__", "Modules", "temp"),
            conditions: list[str] | tuple[str] = ("bugreport", ".zip"),
    ) -> list | None:
        """
        Recognize the files in the specified path. If path does not exist, it will be created,
         and you need to retry the program.
        :param path: specified path
        :param exclude_dir: the directories to exclude scanning
        :param conditions: specified the beginning and end of the file name, only support 2 conditions
        :return: Success => list[str], Failure => None
        """
        if not os.path.exists(path):
            self.log.debug("Specified file does not exist.")
            self.create_dir(path, ignore_tips=True)
            self.log.debug("Specified file has been created.")
            self.log.info(f"Initialize accomplished. Please put your files in {path} directory and try again.")
            return None

        files_list = []
        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if d not in exclude_dir]

            if len(conditions) > 2 or len(conditions) < 2:
                log_error1 = (f"'file_recognition' expects to receive 2 conditions,"
                              f" but there {"is" if len(conditions) == 1 else "are"} conditions.")
                self.log.error(log_error1)
                return None

            for file in files:
                if file.startswith(conditions[0]) and file.endswith(conditions[1]):
                    files_list.append(os.path.join(root, file))

        num = len(files_list)
        if num == 0:
            log_warn1 = f"The specified path {path} does not contain any files."
            self.log.warn(log_warn1)
            return None
        elif num > 0:
            log_info = f"{num} {"file" if num == 1 else "files"} were found."
            self.log.info(log_info)

        return files_list

    def delete_dir(self, path: str, called_by_cmd: bool = True) -> True | False:
        log_debug1 = f"called_by_cmd={called_by_cmd}."
        self.log.debug(log_debug1)

        self.path = path
        self.__empty_path()

        if not os.path.exists(self.path):
            if not called_by_cmd:
                log_error1 = "Directory does not exist."
                self.log.error(log_error1)
                return False

            return True

        try:
            shutil.rmtree(self.path)
        except FileNotFoundError as e:
            log_warn = f"File not found while deleting a directory: {e.strerror}"
            self.log.warn(log_warn)
        except PermissionError as e:
            log_warn = f"Permission error while deleting a directory: {e.strerror}"
            self.log.warn(log_warn)
        except (shutil.Error, OSError) as e:
            log_warn = f"An error occurred while deleting a directory: {e.strerror}"
            self.log.warn(log_warn)
        except Exception as e:
            log_warn = f"An error occurred while deleting a directory: {str(e)}."
            self.log.warn(log_warn)

        if not called_by_cmd:
            log_info = "Directory deleted successfully."
            self.log.info(log_info)
        else:
            log_debug2 = "Directory deleted successfully."
            self.log.debug(log_debug2)

        return True


if __name__ == "__main__":
    pass

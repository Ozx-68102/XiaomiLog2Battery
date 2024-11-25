import os
import pandas as pd
import time

from Modules.LogManager import Log


class Recording:
    def __init__(self, current_path: str) -> None:
        self.current_path = current_path
        self.log_path = os.path.join(self.current_path, "Log")
        self.file_path = os.path.join(self.current_path, "files")
        if not os.path.exists(self.log_path):
            os.makedirs(self.log_path)
        self.log = Log(path=os.path.join(self.log_path, "RecordingLog.txt"))

    def create_csv(self, model: str | None = None) -> None | str:
        """
        Create a csv file in "recorded_data" directory.
        :param model: Internal code of your smartphone, such as Xiaomi 14's internal code is `Houji`.
        :return: Success => `str` , Failure => `None`
        """
        def cc_file(p: str) -> str | None:
            # "Battery time remaining" disabled temporary
            columns = [
                "Estimated battery capacity", "Last learned battery capacity",
                "Min learned battery capacity", "Max learned battery capacity"
            ]

            try:
                df = pd.DataFrame(columns=columns)
                df.index.name = "Log Captured Time"
                df.to_csv(p, index=True, header=True)
                return p
            except FileNotFoundError as er:
                log_error_c = f"File not found: {er.strerror}"
                self.log.error(log_error_c)
                return None
            except PermissionError as er:
                log_error_c = f"Permission denied: {er.strerror}"
                self.log.error(log_error_c)
                return None
            except OSError as er:
                log_error_c = f"An error occurred while creating a DataFrame: {er.strerror}"
                self.log.error(log_error_c)
                return None
            except Exception as er:
                log_error_c = f"An error occurred while creating a DataFrame: {str(er)}"
                self.log.error(log_error_c)
                return None

        csv_dir_path = os.path.join(self.file_path, "recorded_data")
        if not os.path.exists(csv_dir_path):
            os.makedirs(csv_dir_path)

        name = "battery_info.csv"
        name = model + "_" + name if model is not None else name
        csv_path = os.path.join(csv_dir_path, name)

        if os.path.exists(csv_path):
            log_info1 = f"file {os.path.basename(csv_path)} have already exists."
            self.log.info(log_info1)
            time.sleep(0.01)
            ans = None

            while ans not in ["y", "n"]:
                log_debug1 = "Do you want to overwrite this file ([y]/n):"
                self.log.debug(log_debug1)
                ans = input(log_debug1).lower()
                ans = "y" if len(ans) == 0 else ans

                log_debug2 = f"User input: {ans}"
                self.log.debug(log_debug2)

                if ans == "y":
                    try:
                        os.remove(csv_path)
                    except PermissionError as e:
                        log_error = f"Permission denied: {e.strerror}"
                        self.log.error(log_error)
                        return None
                    except FileNotFoundError as e:
                        log_error = f"File not found: {e.strerror}"
                        self.log.error(log_error)
                        return None
                    except OSError as e:
                        log_error = f"An error occurred while remove csv file: {e.strerror}"
                        self.log.error(log_error)
                        return None
                    except Exception as e:
                        log_error = f"An error occurred while remove csv file: {str(e)}"
                        self.log.error(log_error)
                        return None

                    if cc_file(csv_path) is not None:
                        log_info2 = f"File {os.path.basename(csv_path)} has been overwritten."
                        self.log.info(log_info2)
                        return csv_path
                    else:
                        return None

                elif ans == "n":
                    log_info2 = f"File {os.path.basename(csv_path)} has been retained."
                    self.log.info(log_info2)
                    return csv_path
                else:
                    log_warn1 = "Invalid input. Please try again."
                    self.log.warn(log_warn1)
        else:
            if cc_file(csv_path) is not None:
                log_info1 = f"File {os.path.basename(csv_path)} has been created."
                self.log.info(log_info1)
                return csv_path
            else:
                return None

    def __import_data(self, dataf: pd.DataFrame, csv_p: str) -> bool:
        try:
            dataf.to_csv(csv_p, index=True, header=True)
        except FileNotFoundError as e:
            log_warn = f"File not found: {e.strerror}"
            self.log.warn(log_warn)
            return False
        except PermissionError as e:
            log_warn = f"Permission denied: {e.strerror}"
            self.log.warn(log_warn)
            return False
        except OSError as e:
            log_warn = f"An error occurred: {e.strerror}"
            self.log.warn(log_warn)
            return False
        except Exception as e:
            log_warn = f"An error occurred: {str(e)}"
            self.log.warn(log_warn)
            return False

        log_info1 = f"Data imported successfully. Path:{csv_p}"
        self.log.info(log_info1)
        return True

    def data_processing(self, data: dict | list[dict], csv_path: str) -> None | str:
        def check_keys(d: dict) -> bool:
            columns_pre = [
                "Log Captured Time", "Estimated battery capacity", "Last learned battery capacity",
                "Min learned battery capacity", "Max learned battery capacity"
            ]
            missing_keys = [key for key in columns_pre if key not in d]
            if missing_keys:
                log_warn = f"missing keys: {missing_keys}"
                self.log.warn(log_warn)
                return False
            else:
                return True

        if csv_path.isspace():
            log_error = "'csv_path' is empty."
            self.log.error(log_error)
            return None

        if isinstance(data, dict):
            if not check_keys(data):
                return None

            df = pd.DataFrame(data, index=[data["Log Captured Time"]]).drop(data["Log Captured Time"], axis=1)
            df.index.name = "Log Captured Time"

        elif isinstance(data, list):
            if not all(isinstance(d, dict) for d in data):
                temsg = (f"TypeError: The type of 'data' variable expect to receive a dict or a list of dict, "
                         f"not {type(data).__name__}.")
                raise TypeError(temsg)

            if not all(check_keys(d) for d in data):
                return None

            df = pd.DataFrame(data)
            df.set_index("Log Captured Time", inplace=True)

        else:
            temsg = (f"TypeError: The type of 'data' variable expect to receive a dict or a list of dict, "
                     f"not {type(data).__name__}.")
            raise TypeError(temsg)

        csv_data = pd.read_csv(csv_path, index_col="Log Captured Time")

        if csv_data.shape[0] == 0:
            log_info1 = "csv file is empty. So now is preparing to import data."
            self.log.info(log_info1)
            if self.__import_data(df, csv_path):
                return csv_path
            else:
                return None

        cd_copy = csv_data.copy()
        copy_index = cd_copy.index
        new_data = df.loc[~df.index.isin(copy_index)]

        if new_data.empty:
            log_warn1 = "No new unique data to insert."
            self.log.warn(log_warn1)
            return None

        updated_data = pd.concat([new_data, csv_data])

        if self.__import_data(updated_data, csv_path):
            return csv_path
        else:
            return None


if __name__ == "__main__":
    pass

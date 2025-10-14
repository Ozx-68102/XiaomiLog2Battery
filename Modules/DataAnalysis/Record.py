import os
import time

import pandas as pd


class Recording:
    def __init__(self, current_path: str) -> None:
        self.current_path = current_path
        self.file_path = os.path.join(self.current_path, "files")

        self.logger_filename = "Record.txt"
        self.log = Log(filename=self.logger_filename)

    def __df2csv(self, path: str):
        columns = [
            "Estimated battery capacity", "Last learned battery capacity",
            "Min learned battery capacity", "Max learned battery capacity",
            "phone_brand", "nickname", "system_version"
        ]

        try:
            df = pd.DataFrame(columns=columns)
            df.index.name = "Log Captured Time"
            df.to_csv(path, index=True, header=True)
            return path
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

    def __crt_file_centre(self, mdl: str, cdp: str) -> str | None:
        name = f"{mdl}_xiaomi_log_info.csv"
        csv_path = os.path.join(cdp, name)

        if os.path.exists(csv_path):
            log_info1 = f"file {name} have already exists."
            self.log.info(log_info1)
            time.sleep(0.07)

            ans = None
            while ans not in ["y", "n"]:
                log_debug1 = f"Do you want to overwrite {name} ([y]/n):"
                self.log.debug(log_debug1)
                ans = input(log_debug1).lower()
                ans = "y" if len(ans) == 0 else ans

                log_debug2 = f"User input: {ans}"
                self.log.debug(log_debug2)

                if ans == "y":
                    try:
                        os.remove(csv_path)
                    except PermissionError as ecp:
                        log_error = f"Permission error: {ecp.strerror}"
                        self.log.error(log_error)
                        return None
                    except FileNotFoundError as ecp:
                        log_error = f"File not found: {ecp.strerror}"
                        self.log.error(log_error)
                        return None
                    except OSError as ecp:
                        log_error = f"An error occurred while remove csv file: {ecp.strerror}"
                        self.log.error(log_error)
                        return None
                    except Exception as ecp:
                        log_error = f"An error occurred while remove csv file: {str(ecp)}"
                        self.log.error(log_error)
                        return None

                    if self.__df2csv(csv_path) is not None:
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
            if self.__df2csv(csv_path) is not None:
                log_info1 = f"File {os.path.basename(csv_path)} has been created."
                self.log.info(log_info1)
                return csv_path
            else:
                return None

    def create_csv(self, model: set[str] | None = None) -> str | list[str] | None:
        """
        Create a csv file in "recorded_data" directory.
        :param model: Internal code of your smartphone, such as Xiaomi 14's internal code is `Houji`.
        :return: Success => `str` , Failure => `None`
        """
        if not isinstance(model, set):
            try:
                ve_msg = f"ValueError: 'model' expected to receive a set, not '{type(model).__name__}'."
                raise ValueError(ve_msg)
            except ValueError as e:
                self.log.error(str(e))
                return None

        csv_dir_path = os.path.join(self.file_path, "recorded_data")
        os.makedirs(csv_dir_path, exist_ok=True)

        paths = []
        for md in model:
            cp = self.__crt_file_centre(md, csv_dir_path)
            paths.append(cp if cp is not None else "")
        return paths

    def __check_keys(self, data: dict) -> bool:
        columns_pre = [
            "Log Captured Time", "Estimated battery capacity", "Last learned battery capacity",
            "Min learned battery capacity", "Max learned battery capacity", "phone_brand", "nickname", "system_version"
        ]
        missing_keys = [key for key in columns_pre if key not in data]
        if missing_keys:
            log_error_ck = f"missing keys: {missing_keys}"
            self.log.error(log_error_ck)
            return False
        else:
            return True

    def __import_data(self, dataf: pd.DataFrame, csv_p: str) -> bool:
        try:
            dataf.to_csv(csv_p, index=True, header=True)
        except PermissionError as e:
            log_error = f"Permission denied while importing data: {e.strerror}."
            self.log.error(log_error)
            return False
        except OSError as e:
            log_error = f"An error occurred while importing data: {e.strerror}. Path:{csv_p}."
            self.log.error(log_error)
            return False
        except Exception as e:
            log_error = f"An error occurred while importing data: {str(e)}. Path:{csv_p}."
            self.log.error(log_error)
            return False

        log_info1 = f"Data imported successfully. Path:{csv_p}."
        self.log.info(log_info1)
        return True

    def __dp2(self, dts: dict | list[dict], cp: str) -> str | None:
        nickname = os.path.basename(cp).split("_", 1)[0]
        if isinstance(dts, dict):
            if not self.__check_keys(dts):
                return None

            dts = dts if dts["nickname"] == nickname else None
            if dts:
                df = pd.DataFrame(dts, index=[dts["Log Captured Time"]]).drop(dts["Log Captured Time"], axis=1)
                df.index.name = "Log Captured Time"
            else:
                log_error = f"No valid data was found for {nickname}."
                self.log.error(log_error)
                return None

        elif isinstance(dts, list):
            if not all(isinstance(d, dict) for d in dts):
                try:
                    temsg = (f"TypeError: The type of 'data' variable expect to receive a dict or a list of dict, "
                             f"not {type(dts).__name__}.")
                    raise TypeError(temsg)
                except TypeError as e:
                    self.log.error(str(e))
                    return None

            if not all(self.__check_keys(d) for d in dts):
                return None

            dts = [dt for dt in dts if dt["nickname"] == nickname]
            if dts:
                df = pd.DataFrame(dts)
                df.set_index("Log Captured Time", inplace=True)
            else:
                log_error = f"No valid data was found for {nickname}."
                self.log.error(log_error)
                return None

        else:
            try:
                temsg = (f"TypeError: The type of 'data' variable expect to receive a dict or a list of dict, "
                         f"not {type(dts).__name__}.")
                raise TypeError(temsg)
            except TypeError as e:
                self.log.error(str(e))
                return None

        try:
            csv_data = pd.read_csv(cp, index_col="Log Captured Time")
        except pd.errors.EmptyDataError as e:
            log_error = f"The data of specified csv file is empty: {str(e)}. Path:{cp}."
            self.log.error(log_error)
            return None
        except pd.errors.ParserError as e:
            log_error = f"Parser error while reading csv file: {str(e)}. Path:{cp}."
            self.log.error(log_error)
            return None
        except FileNotFoundError as e:
            log_error = f"File not found: {str(e)}."
            self.log.error(log_error)
            return None

        if csv_data.shape[0] == 0:
            log_info1 = "The specified csv file is empty. So now is preparing to import data."
            self.log.info(log_info1)
            if self.__import_data(df, cp):
                return cp
            else:
                return None

        cd_copy = csv_data.copy()
        copy_index = cd_copy.index
        new_data = df.loc[~df.index.isin(copy_index)]

        if new_data.empty:
            log_warn = "No new unique data to insert."
            self.log.warn(log_warn)
            return None

        updated_data = pd.concat([new_data, csv_data])

        if self.__import_data(updated_data, cp):
            return cp
        else:
            return None

    def data_processing(self, data: dict | list[dict], csv_path: str | list[str]) -> str | list[str] | None:
        if isinstance(csv_path, str):
            if csv_path.isspace():
                log_error = "'csv_path' is empty."
                self.log.error(log_error)
                return None

            return self.__dp2(data, csv_path)

        elif isinstance(csv_path, list):
            return [self.__dp2(data, cp) or "" for cp in csv_path]


if __name__ == "__main__":
    pass

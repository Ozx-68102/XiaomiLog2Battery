import os

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import MultipleLocator
from typing import Literal

from Modules.LogManager import Log


class Visualizing:
    def __init__(self, current_path: str):
        self.current_path = current_path
        self.log_path = self.__crt_dir(os.path.join(self.current_path, "Log"))
        self.log = Log(os.path.join(self.log_path, "VisualizingLog.txt"))
        self.filepath = self.__crt_dir(os.path.join(self.current_path, "files"))
        self.csv_path = self.__crt_dir(os.path.join(self.filepath, "recorded_data"))
        self.png_path = self.__crt_dir(os.path.join(self.csv_path, "images"))

    def __crt_dir(self, path: str) -> str | None:
        try:
            if not os.path.exists(path):
                os.makedirs(path)
        except PermissionError as e:
            log_error = f"Permission Error: {e.strerror}"
            self.log.error(log_error)
            return None
        except OSError as e:
            log_error = f"An error occurred while creating directory: {e.strerror}"
            self.log.error(log_error)
            return None
        except Exception as e:
            log_error = f"An error occurred while creating directory: {str(e)}"
            self.log.error(log_error)
            return None

        return path

    def __read_data(self, cname: str) -> pd.DataFrame | None:
        path = os.path.join(self.csv_path, cname)
        try:
            p2df = pd.read_csv(path, sep=",", low_memory=False)
            row = p2df.shape[0]
            col = p2df.shape[1]
            log_info = (f"The data in {row} {"row" if row == 1 else "rows"} and {col} {"col" if col == 1 else "cols"}"
                        f" has been read.")
            self.log.info(log_info)
        except FileNotFoundError as e:
            log_error = f"File not found. Detail: {str(e)}"
            self.log.error(log_error)
            return None
        except pd.errors.EmptyDataError as e:
            log_error = f"Empty Data. Detail: {str(e)}"
            self.log.error(log_error)
            return None
        except pd.errors.ParserError as e:
            log_error = f"Parser Error. Detail: {str(e)}"
            self.log.error(log_error)
            return None
        except Exception as e:
            log_error = f"An error occurred while reading data. Detail: {str(e)}"
            self.log.error(log_error)
            return None

        return p2df

    def __data_filter(self, p2df: pd.DataFrame) -> pd.DataFrame | None:
        cols = ["Log Captured Time", "phone_brand", "nickname", "system_version"]
        try:
            def process_column(col):
                if col.name not in cols:
                    col = col.apply(lambda x: x * 1000 + 500 if isinstance(x, float) and 0 < x < 10 else x)
                    col = col.where((col >= 1000) & (col <= 12000))
                return col

            p2df = p2df.apply(process_column)

            log_debug = "Filtered invalid data."
            self.log.debug(log_debug)

        except Exception as e:
            log_error = f"An error occurred while filtering invalid data. Detail: {str(e)}"
            self.log.error(log_error)
            return None

        return p2df

    def pline_chart(self, path: str | None = None) -> bool:
        df = self.__read_data("battery_info.csv" if path is None else os.path.basename(path))
        df = self.__data_filter(df) if df is not None else df

        png_path = os.path.join(self.png_path, os.path.basename(path).split(".")[0] + ".png") \
            if path is not None else os.path.join(self.png_path, "battery_info.png")

        if df is None:
            log_error = "No data has been found."
            self.log.error(log_error)
            return False

        cols = [
            "Estimated battery capacity", "Last learned battery capacity",
            "Min learned battery capacity", "Max learned battery capacity",
            "nickname"
        ]

        ebc_df = pd.DataFrame(df.loc[:, cols[0]])
        l2bc_df = pd.DataFrame(df.loc[:, cols[1]])
        min_lbc_df = pd.DataFrame(df.loc[:, cols[2]])
        max_lbc_df = pd.DataFrame(df.loc[:, cols[3]])

        log_debug1 = (f"DataFrames were set. Detail: Estimated={ebc_df.shape[0]}, Last Learned={l2bc_df.shape[0]},"
                      f"Min Learned={min_lbc_df.shape[0]}, Max Learned={max_lbc_df.shape[0]}")
        self.log.debug(log_debug1)

        plt.figure(figsize=(10, 6))
        lc_time = df["Log Captured Time"]

        model = df.loc[:, cols[4]].max()

        chart_style: Literal["line chart", "scatter chart"]
        if len(df) == 1:
            log_warn = f"1 data cannot draw a line chart. As a result, it will be replaced by using a scatter plot."
            self.log.warn(log_warn)

            chart_style = "scatter chart"
            plt.scatter(lc_time, ebc_df[cols[0]], label=cols[0], color="blue", marker="o")
            plt.scatter(lc_time, l2bc_df[cols[1]], label=cols[1], color="green", marker="o")
            plt.scatter(lc_time, min_lbc_df[cols[2]], label=cols[2], color="red", marker="o")
            plt.scatter(lc_time, max_lbc_df[cols[3]], label=cols[3], color="orange", marker="o")
        else:
            chart_style = "line chart"
            plt.plot(lc_time, ebc_df[cols[0]], label=cols[0], color="blue", linestyle="--")
            plt.plot(lc_time, l2bc_df[cols[1]], label=cols[1], color="green")
            plt.plot(lc_time, min_lbc_df[cols[2]], label=cols[2], color="red")
            plt.plot(lc_time, max_lbc_df[cols[3]], label=cols[3], color="orange")

        plt.grid(True)
        plt.gca().yaxis.set_major_locator(MultipleLocator(50))
        plt.gca().xaxis.set_major_locator(MultipleLocator(1))

        log_debug2 = f"The grid of {chart_style} was enabled. "
        self.log.debug(log_debug2)

        plt.xlabel("Log Captured Time")
        plt.ylabel("Capacities(mAh)")
        plt.title(f"The battery Capacities of '{model}' Over Time")
        log_debug3 = (f"X axis label: 'Log Captured Time', Y axis label: 'Capacities(mAh)',"
                      f" title: 'Battery Capacities Over Time'")
        self.log.debug(log_debug3)

        plt.legend()
        plt.xticks(rotation=90)
        plt.tight_layout()
        log_debug4 = f"Enabled: legend, xticks(rotation=90), tight_layout()"
        self.log.debug(log_debug4)

        plt.savefig(png_path, dpi=1200)
        log_debug5 = f"Image have been saved at {png_path}."
        self.log.debug(log_debug5)

        log_info = f"Successfully showed the {chart_style}. Path:{png_path}."
        self.log.info(log_info)

        plt.show()

        return True


if __name__ == "__main__":
    pass

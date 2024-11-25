import os

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import MultipleLocator

from Modules.LogManager import Log


class Visualizing:
    def __init__(self, current_path: str):
        def create_dir(path: str):
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

        self.current_path = current_path
        self.log_path = create_dir(os.path.join(self.current_path, "Log"))
        self.log = Log(path=os.path.join(self.log_path, "VisualizingLog.txt"))
        self.filepath = create_dir(os.path.join(self.current_path, "files"))
        self.csv_path = create_dir(os.path.join(self.filepath, "recorded_data"))
        self.png_path = create_dir(os.path.join(self.csv_path, "images"))

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
        try:
            p2df = p2df.apply(lambda col: col.where(col > 10) if col.name != "Log Captured Time" else col)
            log_debug = f"Filtered invalid data."
            self.log.debug(log_debug)
        except Exception as e:
            log_error = f"An error occurred while filtering invalid data. Detail: {str(e)}"
            self.log.error(log_error)
            return None

        return p2df

    def pline_chart(self, path: str | None = None) -> bool:
        df = self.__read_data("battery_info.csv" if path is None else os.path.basename(path))
        df = self.__data_filter(df) if df is not None else df

        if df is None:
            log_error = "No data has been found."
            self.log.error(log_error)
            return False

        cols = [
            "Estimated battery capacity", "Last learned battery capacity",
            "Min learned battery capacity", "Max learned battery capacity"
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
        plt.plot(lc_time, ebc_df[cols[0]], label=cols[0], color="blue")
        plt.plot(lc_time, l2bc_df[cols[1]], label=cols[1], color="green")
        plt.plot(lc_time, min_lbc_df[cols[2]], label=cols[2], color="red")
        plt.plot(lc_time, max_lbc_df[cols[3]], label=cols[3], color="orange")

        plt.grid(True)
        plt.gca().yaxis.set_major_locator(MultipleLocator(25))
        plt.gca().xaxis.set_major_locator(MultipleLocator(1))

        log_debug2 = f"The grid of line chart was enabled. "
        self.log.debug(log_debug2)

        plt.xlabel("Log Captured Time")
        plt.ylabel("Capacities(mAh)")
        plt.title("Battery Capacities Over Time")
        log_debug3 = (f"X axis label: 'Log Captured Time', Y axis label: 'Capacities(mAh)',"
                      f" title: 'Battery Capacities Over Time'")
        self.log.debug(log_debug3)

        plt.legend()
        plt.xticks(rotation=90)
        plt.tight_layout()
        log_debug4 = f"Enabled: legend, xticks(rotation=90), tight_layout()"
        self.log.debug(log_debug4)

        plt.savefig(p := (os.path.join(self.png_path, "battery_capacity.png")), dpi=1200)
        log_debug5 = f"Image have been saved at {p}."
        self.log.debug(log_debug5)

        plt.show()

        return True


if __name__ == "__main__":
    pass

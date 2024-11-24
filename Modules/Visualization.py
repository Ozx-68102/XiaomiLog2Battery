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
                self.log.error(f"Permission Error: {e.strerror}")
                return None
            except OSError as e:
                self.log.error(f"An error occurred while creating directory: {e.strerror}")
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
        # TODO: Lack of some debug log
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

        plt.figure(figsize=(10, 6))

        plt.plot(df["Log Captured Time"], ebc_df[cols[0]], label=cols[0], color="blue")
        plt.plot(df["Log Captured Time"], l2bc_df[cols[1]], label=cols[1], color="green")
        plt.plot(df["Log Captured Time"], min_lbc_df[cols[2]], label=cols[2], color="red")
        plt.plot(df["Log Captured Time"], max_lbc_df[cols[3]], label=cols[3], color="orange")

        plt.grid(True)
        plt.gca().yaxis.set_major_locator(MultipleLocator(25))
        plt.gca().xaxis.set_major_locator(MultipleLocator(1))

        plt.xlabel("Log Captured Time")
        plt.ylabel("Capacities(mAh)")
        plt.title("Battery Capacities Over Time")

        plt.legend()
        plt.xticks(rotation=90)
        plt.tight_layout()

        plt.savefig(os.path.join(self.png_path, "battery_capacity.png"), dpi=1200)

        plt.show()

        return True


if __name__ == "__main__":
    # print(os.path.basename(os.path.join(os.getcwd(), "A.py")))
    a = os.path.dirname(os.getcwd())
    v = Visualizing(a)
    v.pline_chart()

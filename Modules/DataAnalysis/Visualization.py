import os
from typing import Literal

import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import Line, Scatter, Grid
from pyecharts.globals import ThemeType

from Modules.LogRecord import Log


class Visualizing:
    def __init__(self, current_path: str):
        self.current_path = current_path

        self.logger_filename = "Visualizing.txt"
        self.log = Log(filename=self.logger_filename)

        self.filepath = self.__crt_dir(os.path.join(self.current_path, "files"))
        self.csv_path = self.__crt_dir(os.path.join(self.filepath, "recorded_data"))
        self.charts_path = self.__crt_dir(os.path.join(self.csv_path, "images"))

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

    def __read_data(self, csv_name: str) -> pd.DataFrame | None:
        path = os.path.join(self.csv_path, csv_name)
        try:
            p2df = pd.read_csv(path, sep=",", low_memory=False)
            row = p2df.shape[0]
            col = p2df.shape[1]
            log_info = f"The data has been read. Row(s)/Column(s): {row}/{col}."
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

    def pline_chart(self, filepath: str) -> bool:
        if filepath.isspace() or filepath is None:
            log_error = f"'filepath' can not be a space or a 'NoneType'."
            self.log.error(log_error)
            return False

        df = self.__data_filter(self.__read_data(os.path.basename(filepath)))

        if df is None:
            log_error = "No data has been found."
            self.log.error(log_error)
            return False

        html_path = os.path.join(self.charts_path, os.path.basename(filepath).split(".")[0] + ".html")

        cols = [
            "Estimated battery capacity", "Last learned battery capacity",
            "Min learned battery capacity", "Max learned battery capacity",
            "nickname"
        ]

        try:
            ebc_data = df.loc[:, cols[0]].tolist()
            l2bc_data = df.loc[:, cols[1]].tolist()
            min_lbc_data = df.loc[:, cols[2]].tolist()
            max_lbc_data = df.loc[:, cols[3]].tolist()

            whole_data = ebc_data + l2bc_data + min_lbc_data + max_lbc_data
            yaxis_max_value = int(max(whole_data) * 1.02)
            yaxis_min_value = int(min(whole_data) * 0.98)

            lc_time = df["Log Captured Time"].tolist()

            avg_last_learned = sum(l2bc_data) / len(l2bc_data)
            avg_min_learned = sum(min_lbc_data) / len(min_lbc_data)
            avg_max_learned = sum(max_lbc_data) / len(max_lbc_data)

            avg_battery_capacity = round((avg_last_learned + avg_min_learned + avg_max_learned) / 3)

            model = df[cols[4]].iloc[0]

            log_info1 = f"INFORMATION => Model: {model}, Average battery capacity: {avg_battery_capacity} mAh."
            self.log.info(log_info1)

        except Exception as e:
            self.log.error(f"Error processing data: {e}")
            return False

        chart_name: Literal["Scatter", "Line"]
        if len(df) == 1:
            log_warn = f"Only 1 data cannot draw a line chart. Instead, it will be replaced by using a scatter plot."
            self.log.warn(log_warn)

            chart_name = "Scatter"

            # Scatter plot for single data point
            chart = Scatter(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))
            chart.add_xaxis(lc_time)
            chart.add_yaxis(cols[0], ebc_data, symbol="circle", label_opts=opts.LabelOpts(is_show=False))
            chart.add_yaxis(cols[1], l2bc_data, symbol="triangle", label_opts=opts.LabelOpts(is_show=False))
            chart.add_yaxis(cols[2], min_lbc_data, symbol="diamond", label_opts=opts.LabelOpts(is_show=False))
            chart.add_yaxis(cols[3], max_lbc_data, symbol="square", label_opts=opts.LabelOpts(is_show=False))
        else:
            chart_name = "Line"
            # Line chart for multiple data points
            chart = Line(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))
            chart.add_xaxis(lc_time)
            chart.add_yaxis(cols[0], ebc_data, is_smooth=True, linestyle_opts=opts.LineStyleOpts(width=2), label_opts=opts.LabelOpts(is_show=False))
            chart.add_yaxis(cols[1], l2bc_data, is_smooth=True, linestyle_opts=opts.LineStyleOpts(width=2), label_opts=opts.LabelOpts(is_show=False))
            chart.add_yaxis(cols[2], min_lbc_data, is_smooth=True, linestyle_opts=opts.LineStyleOpts(width=2), label_opts=opts.LabelOpts(is_show=False))
            chart.add_yaxis(cols[3], max_lbc_data, is_smooth=True, linestyle_opts=opts.LineStyleOpts(width=2), label_opts=opts.LabelOpts(is_show=False))

        # Add average line
        chart.set_global_opts(
            title_opts=opts.TitleOpts(
                title=f"Battery Capacities of '{model}' Over Time",
                pos_left="center",
                pos_top="top",
            ),
            xaxis_opts=opts.AxisOpts(
                name="Captured Time",
                name_textstyle_opts=opts.TextStyleOpts(font_size=10),
                axislabel_opts=opts.LabelOpts(
                    rotate=30, interval=4, font_size=12
                )
            ),
            yaxis_opts=opts.AxisOpts(
                name="Capacities (mAh)",
                name_textstyle_opts=opts.TextStyleOpts(font_size=10),
                max_=yaxis_max_value,
                min_=yaxis_min_value
            ),
            tooltip_opts=opts.TooltipOpts(trigger="axis"),
            datazoom_opts=[opts.DataZoomOpts(pos_bottom="5%")],  # Zoom option for better viewing, but temporary banned at the moment
            legend_opts = opts.LegendOpts(
                orient="horizontal",
                pos_top="5%",  # Place legend at the bottom
                pos_left="center",
            )
        )
        chart.add_yaxis(
            "Average battery capacity",
            [avg_battery_capacity] * len(lc_time),
            linestyle_opts=opts.LineStyleOpts(type_="dashed", width=2, color="magenta"),
            is_symbol_show=False
        )

        grid = Grid(init_opts=opts.InitOpts(width="825px",height="625px"))
        grid.add(chart, grid_opts=opts.GridOpts(pos_top="18%", pos_bottom="25%")) # charts position, not include title

        grid.render(html_path)
        log_info = f"{chart_name} chart has been saved to {html_path}."
        self.log.info(log_info)

        return True

if __name__ == "__main__":
    pass

import json
import os
from typing import Literal

import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import Line, Scatter, Pie, Grid
from pyecharts.globals import ThemeType

from Modules.LogRecord import Log


class Visualizing:
    def __init__(self, current_path: str):
        self.current_path = current_path

        self.logger_filename = "Visualization.txt"
        self.log = Log(filename=self.logger_filename)

        # TODO: gonna be obsolete in the future
        self.filepath = self.__crt_dir(os.path.join(self.current_path, "files"))
        self.csv_path = self.__crt_dir(os.path.join(self.filepath, "recorded_data"))
        self.charts_path = self.__crt_dir(os.path.join(self.csv_path, "charts"))

        self.model_caps = self.read_capacities_json()  # model capacities

    @staticmethod
    def read_capacities_json() -> dict[str, dict[str, int] | int]:
        if not hasattr(Visualizing, "_cached_capacities_json"):
            filepath = os.path.join(os.path.dirname(__file__), "XiaomiBatteryCapacities_Android13Plus.json")
            with open(file=filepath, mode="r") as capacities_file:
                Visualizing._cached_capacities_json = json.load(capacities_file)
        return Visualizing._cached_capacities_json

    def __crt_dir(self, path: str) -> str | None:
        try:
            os.makedirs(name=path, exist_ok=True)
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
        def process_column(col):
            if col.name not in ("Log Captured Time", "phone_brand", "nickname", "system_version"):
                col = col.apply(lambda x: x * 1000 + 500 if isinstance(x, float) and 0 < x < 10 else x)
                col = col.where((col >= 1000) & (col <= 12000))
            return col

        path = os.path.join(self.csv_path, csv_name)
        try:
            p2df = pd.read_csv(path, sep=",", low_memory=False).apply(process_column)
            log_info = f"The data has been read. Row(s)/Column(s): {p2df.shape[0]}/{p2df.shape[1]}."
            self.log.info(log_info)
        except FileNotFoundError as e:
            log_error = f"File not found while reading data. Details: {str(e)}"
            self.log.error(log_error)
            return None
        except pd.errors.EmptyDataError as e:
            log_error = f"An Empty Data occurred while reading data. Details: {str(e)}"
            self.log.error(log_error)
            return None
        except pd.errors.ParserError as e:
            log_error = f"Parser Error while reading data. Details: {str(e)}"
            self.log.error(log_error)
            return None
        except Exception as e:
            log_error = f"An error occurred while reading data. Details: {str(e)}"
            self.log.error(log_error)
            return None

        return p2df

    def diagrams_generator(self, filepath: str) -> list[int]:
        def average_count(values: list) -> float:
            return float(sum(values) / len(values))

        def dataframe2list(df: pd.DataFrame, column: str) -> list[int]:
            return df.loc[:, column].tolist()

        count = [0, 0]  # success, failure

        if filepath.isspace() or filepath is None:
            log_error = f"An error occurred while generating diagrams. Details: 'filepath' can not be a space or a 'NoneType'."
            self.log.error(log_error)
            return count

        dataframe = self.__read_data(os.path.basename(filepath))

        if dataframe is None:
            log_error = "No data has been found when trying to generate diagram."
            self.log.error(log_error)
            return count

        cols = [
            "Estimated battery capacity", "Last learned battery capacity",
            "Min learned battery capacity", "Max learned battery capacity", "nickname"
        ]

        try:
            lc_time = dataframe["Log Captured Time"].tolist()

            ebc_data = dataframe2list(df=dataframe, column=cols[0])
            l2bc_data = dataframe2list(df=dataframe, column=cols[1])
            min_lbc_data = dataframe2list(df=dataframe, column=cols[2])
            max_lbc_data = dataframe2list(df=dataframe, column=cols[3])

            avg_last_learned = average_count(values=l2bc_data)
            avg_min_learned = average_count(values=min_lbc_data)
            avg_max_learned = average_count(values=max_lbc_data)

            avg_battery_capacity = int(round((avg_last_learned + avg_min_learned + avg_max_learned) / 3))

            model = str(dataframe[cols[4]].iloc[0])

            log_info1 = f"INFORMATION => Model: {model}, Average battery capacity: {avg_battery_capacity} mAh."
            self.log.info(log_info1)
        except Exception as e:
            self.log.error(f"An error occurred while generating diagrams. Details: {e}")
            return count

        data_gene_bc_chart = {
            "basic_columns": cols,
            "data_length": len(dataframe),
            "ebc_data": ebc_data,
            "l2bc_data": l2bc_data,
            "avg_battery_capacity": avg_battery_capacity,
            "min_lbc_data": min_lbc_data,
            "max_lbc_data": max_lbc_data,
            "lc_time": lc_time,
            "model": model,
        }

        if self._generate_battery_changing_chart(data=data_gene_bc_chart):
            count[0] += 1
        else:
            count[1] += 1

        if isinstance(self.model_caps[model], dict):
            for key, value in self.model_caps[model].items():
                data_gene_bh_chart = {
                    "name": f"{model}_{key}_version_battery_health_chart.html",
                    "avg_bc": avg_battery_capacity,
                    "max_bc": self.model_caps[model][key]
                }
                if self._generate_battery_health_chart(data=data_gene_bh_chart):
                    count[0] += 1
                else:
                    count[1] += 1
        else:
            data_gene_bh_chart = {
                "name": f"{model}_battery_health_chart.html",
                "model": model,
                "avg_bc": avg_battery_capacity,
                "max_bc": self.model_caps[model]
            }

            if self._generate_battery_health_chart(data=data_gene_bh_chart):
                count[0] += 1
            else:
                count[1] += 1

        return count

    def _generate_battery_changing_chart(self, data: dict) -> bool:
        try:
            cols = list(data["basic_columns"])

            whole_data = data["ebc_data"] + data["l2bc_data"] + data["min_lbc_data"] + data["max_lbc_data"]
            yaxis_max_value = int(max(whole_data) * 1.02)
            yaxis_min_value = int(min(whole_data) * 0.98)

            chart_name: Literal["Scatter", "Line"]
            if data["data_length"] == 1:
                log_warn = f"Only 1 data cannot draw a line chart. Instead, it will be replaced by using a scatter plot."
                self.log.warn(log_warn)

                chart_name = "Scatter"

                # Scatter plot for single data point
                chart = Scatter(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))
                chart.add_xaxis(data["lc_time"])
                chart.add_yaxis(cols[0], data["ebc_data"], symbol="circle", label_opts=opts.LabelOpts(is_show=False))
                chart.add_yaxis(cols[1], data["l2bc_data"], symbol="triangle", label_opts=opts.LabelOpts(is_show=False))
                chart.add_yaxis(cols[2], data["min_lbc_data"], symbol="diamond",
                                label_opts=opts.LabelOpts(is_show=False))
                chart.add_yaxis(cols[3], data["max_lbc_data"], symbol="square",
                                label_opts=opts.LabelOpts(is_show=False))
            else:
                chart_name = "Line"
                # Line chart for multiple data points
                chart = Line(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))
                chart.add_xaxis(data["lc_time"])
                chart.add_yaxis(cols[0], data["ebc_data"], is_smooth=True, linestyle_opts=opts.LineStyleOpts(width=2),
                                label_opts=opts.LabelOpts(is_show=False))
                chart.add_yaxis(cols[1], data["l2bc_data"], is_smooth=True, linestyle_opts=opts.LineStyleOpts(width=2),
                                label_opts=opts.LabelOpts(is_show=False))
                chart.add_yaxis(cols[2], data["min_lbc_data"], is_smooth=True,
                                linestyle_opts=opts.LineStyleOpts(width=2), label_opts=opts.LabelOpts(is_show=False))
                chart.add_yaxis(cols[3], data["max_lbc_data"], is_smooth=True,
                                linestyle_opts=opts.LineStyleOpts(width=2), label_opts=opts.LabelOpts(is_show=False))

            # Add average line
            chart.set_global_opts(
                title_opts=opts.TitleOpts(
                    title=f"Battery Capacities of '{data["model"]}' Over Time",
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
                datazoom_opts=[opts.DataZoomOpts(pos_bottom="5%")],
                # Zoom option for better viewing, but temporary banned at the moment
                legend_opts=opts.LegendOpts(
                    orient="horizontal",
                    pos_top="5%",  # Place legend at the bottom
                    pos_left="center",
                )
            )
            chart.add_yaxis(
                "Average battery capacity",
                [data["avg_battery_capacity"]] * len(data["lc_time"]),
                linestyle_opts=opts.LineStyleOpts(type_="dashed", width=2, color="magenta"),
                is_symbol_show=False
            )

            grid = Grid(init_opts=opts.InitOpts(width="825px", height="625px"))
            grid.add(chart,
                     grid_opts=opts.GridOpts(pos_top="18%", pos_bottom="25%"))  # charts position, not include title

            html_file_name = data["model"] + "_battery_changing_chart.html"
            save_path = os.path.join(self.charts_path, html_file_name)
            grid.render(path=save_path)
            log_info = f"{chart_name} chart has been saved to {save_path}."
            self.log.info(log_info)
        except KeyError as e:
            log_error = f"A KeyError occurred while generating battery changing chart. Details: {e}."
            self.log.error(log_error)
            return False
        except ValueError as e:
            log_error = f"A ValueError occurred while generating battery changing chart. Details: {e}."
            self.log.error(log_error)
            return False
        except OSError as e:
            log_error = f"A File system error occurred while generating battery changing chart. Details: {e}."
            self.log.error(log_error)
            return False
        except Exception as e:
            log_error = f"An unexpected error occurred while generating battery changing chart. Details: {e}."
            self.log.error(log_error)
            return False

        return True

    def _generate_battery_health_chart(self, data: dict) -> bool:
        try:
            current_capacity = data["avg_bc"]
            typical_capacity = data["max_bc"]

            health_percentage = float(round(current_capacity / typical_capacity * 100, 1))
            lost_percentage = round(100 - health_percentage, 1)

            chart_data = [("Remaining Capacity Percentage", health_percentage)]

            if health_percentage >= 85:
                health_color = "#00CE3F"  # green
            elif 80 <= health_percentage < 85:
                health_color = "#FFA500"  # orange
            elif 60 <= health_percentage < 80:
                health_color = "#FFFF00"  # yellow
            else:
                health_color = "#FF0000"  # red

            if health_percentage < 100:
                chart_data.append(("Lost Capacity Percentage", lost_percentage))

            chart = Pie(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))
            chart.add("", chart_data, radius=["50%", "70%"], label_opts=opts.LabelOpts(is_show=False), is_clockwise=False)
            chart.set_colors([health_color, "#999999"])
            chart.set_global_opts(
                title_opts=opts.TitleOpts(
                    title=f"Battery Health of '{data["model"]}'\n{current_capacity} mAh / {typical_capacity} mAh ({health_percentage}%)",
                    pos_left="center",
                    pos_top="middle",
                    title_textstyle_opts=opts.TextStyleOpts(
                        font_size=15,
                        color="black",
                        font_weight="bold"
                    ),
                ),
                legend_opts=opts.LegendOpts(is_show=False),
            )

            save_path = os.path.join(self.charts_path, data["name"])
            chart.render(path=save_path)
            log_info = f"Pie chart of {data['model']} has been saved to {save_path}."
            self.log.info(log_info)

        except KeyError as e:
            log_error = f"A KeyError occurred while generating battery health chart. Details: {e}."
            self.log.error(log_error)
            return False
        except ZeroDivisionError as e:
            log_error = f"A ZeroDivisionError occurred while generating battery health chart. Details: {e}."
            self.log.error(log_error)
            return False
        except (TypeError, ValueError) as e:
            log_error = f"A Data error occurred while generating battery health chart. Details: {e}."
            self.log.error(log_error)
            return False
        except OSError as e:
            log_error = f"A File system error occurred while generating battery health chart. Details: {e}."
            self.log.error(log_error)
            return False
        except Exception as e:
            log_error = f"An unexpected error occurred while generating battery health chart. Details: {e}."
            self.log.error(log_error)
            return False

        return True


if __name__ == "__main__":
    pass

import json
import os

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from Modules.DataAnalysis import BatteryDataService
from Modules.Database import DB_FIELDS


class PlotlyVisualizer:
    def __init__(self):
        self.model_caps = self._load_standard_caps()
        self.data_service = BatteryDataService()

        self.capacity_fields = [field for field in DB_FIELDS if "battery_capacity" in field]

        # reasonable capacity range
        self.min_valid_cap = 1000
        self.max_valid_cap = 15000  # Remember to maintenance

    @staticmethod
    def _load_standard_caps() -> dict[str, dict[str, int] | int]:
        if hasattr(PlotlyVisualizer, "_cached_standard_caps"):
            return PlotlyVisualizer._cached_standard_caps

        json_path = os.path.join(os.path.dirname(__file__), "XiaomiBatteryCapacities_Android13Plus.json")
        if not os.path.exists(json_path):
            raise FileNotFoundError(f"Cannot find the json file: {os.path.basename(json_path)}.")

        with open(file=json_path, mode="r", encoding="utf-8") as json_file:
            PlotlyVisualizer._cached_standard_caps = json.load(json_file)

        return PlotlyVisualizer._cached_standard_caps

    def _preprocess_data(self, raw_data: list[dict[str, str | int]]) -> pd.DataFrame:
        if not raw_data:
            raise ValueError("No data provided.")

        df = pd.DataFrame(raw_data)
        df["log_capture_time"] = pd.to_datetime(df.loc[:, "log_capture_time"], format="%Y-%m-%d %H:%M:%S")
        for field in self.capacity_fields:
            df[field] = pd.to_numeric(df[field], errors="coerce")  # invalid value will be converted to NaN

        df = df[(df[self.capacity_fields] >= self.min_valid_cap).all(axis=1) & (
                df[self.capacity_fields] <= self.max_valid_cap).all(axis=1) & df["nickname"].notna()]

        df = df.sort_values(by="log_capture_time", ascending=False).reset_index(drop=True)
        if df.empty:
            raise ValueError("No valid data provided.")

        return df

    def gen_battery_changing_chart(self, data: list[dict[str, str | int]]) -> go.Figure:
        """
        Generate a line/scatter chart of the battery capacity change.
        :param data: Battery data.
        """
        df = self._preprocess_data(data)
        model = df.loc[:, "nickname"].iloc[0]

        df["avg_battery_capacity"] = df[self.capacity_fields].mean(axis=1)

        fig = make_subplots(rows=1, cols=1, subplot_titles=[f"Battery Capacities of {model} Over Time"],
                            vertical_spacing=0.15)

        marker_symbols = ["circle", "triangle-up", "diamond", "square"]
        for index, field in enumerate(self.capacity_fields):
            if len(df) == 1:
                fig.add_trace(
                    go.Scatter(
                        x=df["log_capture_time"],
                        y=df[field],
                        name=field,
                        mode="markers",
                        marker={"symbol": marker_symbols[index], "size": 10},
                        showlegend=True
                    ),
                    row=1, col=1
                )
            else:
                fig.add_trace(
                    go.Scatter(
                        x=df["log_capture_time"],
                        y=df[field],
                        name=field,
                        mode="lines",
                        line={"width": 2, "shape": "spline"},
                        showlegend=True
                    ),
                    row=1, col=1
                )

        fig.add_trace(
            go.Scatter(
                x=df["log_capture_time"],
                y=df["avg_battery_capacity"],
                name="Average Capacity",
                mode="lines",
                line={"width": 2, "dash": "dash", "color": "magenta"},
                showlegend=False
            ),
            row=1, col=1
        )

        fig.update_layout(
            height=600, width=800,
            legend={"orientation": "h", "yanchor": "top", "y": 1.2, "xanchor": "center", "x": 0.5},
            xaxis={"tickangle": 30, "tickmode": "auto", "nticks": 10},
            yaxis={
                "range": [
                    df[self.capacity_fields].min() * 0.98,
                    df[self.capacity_fields].max() * 1.02
                ]},
            hovermode="x unified"
        )

        return fig

    def gen_battery_health_chart(self, data: list[dict[str, str | int]]) -> go.Figure:
        df = self._preprocess_data(data)
        lastest_10df = df.head(10).copy()
        model = str(df.loc[:, "nickname"].iloc[0])

        lastest_10df.loc[:, "single_composite_capacity"] = lastest_10df.loc[:, self.capacity_fields].mean(axis=1)
        current_avg_cap = lastest_10df.loc[:, "single_composite_capacity"].mean()
        current_avg_cap = round(current_avg_cap, 0)

        model_standard_cap = self.model_caps.get(model)
        if not model_standard_cap:
            raise ValueError(f"Cannot find standard capacity of model '{model}'.")

        if isinstance(model_standard_cap, dict):
            model_standard_cap = next(iter(model_standard_cap.values()))  # TODO: Extent functions here in the future

        health_percent = round((current_avg_cap / model_standard_cap) * 100, 2)
        health_percent = 0 if health_percent < 0 else health_percent
        if health_percent >= 100:
            lost_percent = 0
        elif health_percent <= 0:
            lost_percent = 100
        else:
            lost_percent = round(100 - health_percent, 2)

        if health_percent >= 85:
            health_color = "#00CE3F"  # Green
        elif 80 <= health_percent < 85:
            health_color = "#FFA500"  # Orange
        elif 60 <= health_percent < 80:
            health_color = "#FFFF00"  # Yellow
        else:
            health_color = "#FF0000"  # Red

        fig = go.Figure(
            data=[go.Pie(
                labels=["Remaining Capacity", "Lost Capacity"],
                values=[health_percent, lost_percent],
                hole=0.5,
                marker={
                    "colors": [health_color, "#999999"],
                    "line": {"color": "white", "width": 2}
                },
                textinfo="label+percent",
                textfont={"size": 12, "weight": "bold"},
                hoverinfo="value+percent"
            )]
        )

        fig.update_layout(
            height=500, width=500,
            title={
                "text": f"Battery Health of {model}<br />Current Capacity: {int(current_avg_cap)} / {int(model_standard_cap)} mAh<br />Health: {health_percent}%",
                "x": 0.5, "y": 0.5, "font": {"size": 14, "weight": "bold"}
            }, showlegend=False
        )

        return fig


if __name__ == "__main__":
    pass
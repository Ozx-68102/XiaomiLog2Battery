import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.analysis import DataServices
from src.config import BATTERY_CAPACITY_TYPES


class Visualizer:
    def __init__(self):
        self.ds = DataServices()
        self.cap_fields = BATTERY_CAPACITY_TYPES + ["hardware_capacity"]
        self.avg_fields = [field for field in self.cap_fields if field != "estimated_battery_capacity"]

        self.cap_range = (1000, 15000)

    def _preprocess(self, raw: list[dict[str, str | int]]) -> pd.DataFrame:
        if not raw:
            raise ValueError("No data provided.")

        df = pd.DataFrame(raw)
        df["log_capture_time"] = pd.to_datetime(df.loc[:, "log_capture_time"], format="%Y-%m-%d %H:%M:%S")
        for field in self.cap_fields:
            df[field] = pd.to_numeric(df[field], errors="coerce")

        df = df[
            (df[self.cap_fields] >= self.cap_range[0]).all(axis=1) &
            (df[self.cap_fields] <= self.cap_range[1]).all(axis=1) &
            df["nickname"].notna()
        ]
        df = df.sort_values(by="log_capture_time", ascending=False).reset_index(drop=True)
        if df.empty:
            raise ValueError("No valid data provided.")
        
        return df

    @staticmethod
    def _calculate_battery_health(cap_num: float, model_cap: float) -> dict[str, str | float]:
        health_percent = round((cap_num / model_cap) * 100, 2)
        health_percent = 0.00 if health_percent < 0 else health_percent

        lost_percent = 0.00 if health_percent >= 100 else round(100 - health_percent, 2)

        if health_percent >= 85:
            health_color = "#00CE3F"  # Green
        elif 80 <= health_percent < 85:
            health_color = "#FFA500"  # Orange
        elif 60 <= health_percent < 80:
            health_color = "#FFFF00"  # Yellow
        else:
            health_color = "#FF0000"  # Red

        return {
            "lost_percent": lost_percent,
            "health_color": health_color,
            "health_percent": health_percent
        }

    def gen_battery_changing_chart(self, data: list[dict[str, str | int]]) -> go.Figure:
        df = self._preprocess(raw=data)
        model = str(df.loc[:, "nickname"].iloc[0])

        df["avg_battery_capacity"] = df[self.avg_fields].mean().mean()

        fig = make_subplots(
            rows=1, cols=1,
            subplot_titles=[f"Battery Capacities of {model} Over Time"],
            vertical_spacing=0.15
        )

        marker_symbols = ["circle", "triangle-up", "diamond", "square", "pentagon"]
        for index, field in enumerate(self.cap_fields):
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
                continue

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
            yaxis={"range": [df[self.cap_fields].min() * 0.98, df[self.cap_fields].max() * 1.02]},
            hovermode="x unified"
        )

        return fig

    
    def gen_battery_health_chart(self, data: list[dict[str, str | int]]) -> go.Figure:
        df = self._preprocess(raw=data)

        model = str(df.loc[:, "nickname"].iloc[0])
        if "design_capacity" not in df.columns and not df["design_capacity"].notna().any():
            raise ValueError(f"Cannot find design capacity for model '{model}'. Please ensure hardware data is parsed correctly.")

        last_20df: pd.DataFrame = df.head(20).copy()  # noqa
        last_20df.loc[:, "avg_cap"] = last_20df.loc[:, self.avg_fields].mean()
        avg_cap = float(last_20df.loc[:, "avg_cap"].mean())
        avg_cap = round(avg_cap, 2)

        standard_cap = df["design_capacity"].dropna().iloc[0]
        health_data = self._calculate_battery_health(cap_num=avg_cap, model_cap=standard_cap)

        fig = go.Figure(
            data=[
                go.Pie(
                    labels=["Remaining Capacity", "Lost Capacity"],
                    values=[health_data["health_percent"], health_data["lost_percent"]],
                    hole=0.5,
                    marker={
                        "colors": [health_data["health_color"], "#999999"],
                        "line": {"color": "white", "width": 2}
                    },
                    textinfo="label+percent",
                    textfont={"size": 12, "weight": "bold"},
                    hoverinfo="value+percent"
                )
            ]
        )

        fig.update_layout(
            height=500,
            width=500,
            title={
                "text": f"Battery Health of {model}<br />Current Capacity: {int(avg_cap)} / {int(standard_cap)} mAh<br />Health: {health_data["health_percent"]}%",
                "x": 0.5, "y": 0.5,
                "font": {"size": 14, "weight": "bold"}
            },
            showlegend=False
        )

        return fig


import dash
import dash_ag_grid as dag
import dash_bootstrap_components as dbc
import pandas as pd
from dash import html, Input, Output, State, no_update

from src.analysis import DataServices

dash.register_page(__name__, path="/reports", order=5, name="Reports")


def get_general_card(title: str, value: str | int, icon: str, color: str) -> dbc.Col:
    return dbc.Col([
        dbc.Card([
            dbc.CardBody([
                html.Div([
                    html.I(className=f"bi {icon} fs-1 text-{color} me-3"),
                    html.Div([
                        html.H6(title, className="text-muted mb-1"),
                        html.H4(value, className="fw-bold mb-0")
                    ]),
                ], className="d-flex align-items-center"),
            ]),
        ], class_name="shadow-sm h-100 border-0 border-start border-4")
    ], width=12, sm=6, lg=3, class_name="mb-3")


def layout():
    models = DataServices().get_model() or []
    default_val = models[0] if models else None

    column_defs = [
        {
            "field": "display_time",
            "headerName": "Log Capture Time",
            "sortable": True,
            "filter": True,
            "minWidth": 180,
            "pinned": "left"
        },
        {
            "headerName": "Capacity Metrics (mAh)",
            "headerClass": "bg-light text-center fw-bold",
            "children": [
                {
                    "field": "hardware_capacity",
                    "headerName": "Actual/Hardware",
                    "sortable": True,
                    "filter": "agNumberColumnFilter",
                    "columnGroupShow": "closed"
                },
                {
                    "field": "design_capacity",
                    "headerName": "Design",
                    "sortable": True,
                    "filter": "agNumberColumnFilter",
                    "columnGroupShow": "closed"
                },
                {
                    "field": "estimated_battery_capacity",
                    "headerName": "Estimated",
                    "sortable": True,
                    "filter": "agNumberColumnFilter"
                },
                {
                    "field": "last_learned_battery_capacity",
                    "headerName": "Last Learned",
                    "sortable": True,
                    "filter": "agNumberColumnFilter"
                },
                {
                    "field": "min_learned_battery_capacity",
                    "headerName": "Min Learned",
                    "sortable": True,
                    "filter": "agNumberColumnFilter"
                },
                {
                    "field": "max_learned_battery_capacity",
                    "headerName": "Max Learned",
                    "sortable": True,
                    "filter": "agNumberColumnFilter"
                },
            ],
        },
        {
            "field": "cycle_count",
            "headerName": "Cycles",
            "sortable": True,
            "filter": "agNumberColumnFilter"
        },
        {
            "field": "health_snapshots",
            "headerName": "Health (%)",
            "sortable": True,
            "filter": "agNumberColumnFilter",
            "cellStyle": {
                "styleConditions": [
                    {"condition": "params.value < 80", "style": {"color": "#dc3545", "fontWeight": "bold"}},  # Red
                    {"condition": "params.value >= 80", "style": {"color": "#198754", "fontWeight": "bold"}}  # Green
                ],
            },
        },
        {
            "field": "system_version",
            "headerName": "OS Version",
            "sortable": True,
            "filter": True
        },
    ]

    return [
        dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.Label("Select Model", className="fw-bold"),
                        dbc.Select(
                            id="reports-model-selector",
                            options=[{"label": "Select a model to continue", "value": ""}] + [{"label": n, "value": n}
                                                                                              for n in models],
                            value=default_val,
                            placeholder="Select a device modal..."
                        ),
                    ], width=12, md=4),
                ]),
            ]),
        ]),
        html.Br(),
        dbc.Row(id="reports-general-container", class_name="mb-2"),
        html.Br(),
        dbc.Card([
            dbc.CardHeader([
                html.I(className="bi bi-table me-2"),
                "Detailed Records"
            ]),
            dbc.CardBody([
                dag.AgGrid(
                    id="reports-data-grid",
                    columnDefs=column_defs,
                    rowData=[],
                    defaultColDef={
                        "resizable": True,
                        "filter": True,
                        "sortable": True,
                        "floatingFilter": True
                    },
                    columnSize="sizeToFit",
                    dashGridOptions={
                        "pagination": True,
                        "paginationPageSize": 20,
                        "animateRows": True
                    },
                    style={"height": "600px"},
                    className="ag-theme-alpine",
                )
            ], class_name="p-0"),
        ], class_name="shadow-sm"),
    ]


@dash.callback(
    [
        Output("reports-general-container", "children"),
        Output("reports-data-grid", "rowData"),
    ],
    Input("reports-model-selector", "value"),
    State("global-timezone", "data")
)
def update_report(model: str, timezone: str) -> tuple[dbc.Col, list[dict[str, str | int | float]]]:
    if not model:
        return no_update, []

    raw_data = DataServices().get_battery_data("analysis_results", model=model, health_snapshots=True)
    if not raw_data:
        return no_update, []

    df = pd.DataFrame(raw_data)

    utc_series = pd.to_datetime(df["log_capture_time"], unit="s", utc=True)
    df["display_time"] = utc_series.dt.tz_convert(tz=timezone).dt.tz_localize(None).dt.strftime("%Y-%m-%d %H:%M:%S")  # noqa

    latest_data = df.iloc[0]

    current_health = latest_data.get("health_snapshots", 0.0)
    if current_health >= 80:
        color = "success"
    elif current_health >= 60:
        color = "warning"
    else:
        color = "danger"

    general_cards = [
        get_general_card("Last Capture Time", latest_data["display_time"], "bi-clock-history", "primary"),
        get_general_card("Current Cycle Count", latest_data["cycle_count"], "bi-arrow-repeat", "info"),
        get_general_card("Design Capacity", f"{latest_data["design_capacity"]} mAh", "bi-battery-full", "secondary"),
        get_general_card("Latest Health Snapshot", f"{current_health}%", "bi-heart-pulse-fill", color)
    ]

    return general_cards, df.to_dict("records")  # noqa

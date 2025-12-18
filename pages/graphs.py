import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State, no_update
from dash.development.base_component import Component

from src import DataServices, Visualizer
from utils import format_alert_content

dash.register_page(__name__, path="/graphs", order=4, name="Graphs")


def layout() -> list[Component]:
    model = DataServices().get_model() or []
    default_val = model[0] if model else None
    is_disabled = False if default_val else True

    return [
        dbc.Card([
            dbc.CardHeader(html.H5("Visualization Settings", className="m-0")),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Select Device Model", class_name="fw-bold"),
                        dbc.Select(
                            id="model-selector",
                            options=[{"label": "Select a model to continue", "value": ""}] + [{"label": n, "value": n} for n in model],
                            value=default_val,
                            class_name="mb-3"
                        ),
                    ], width=12, md=8),
                    dbc.Col([
                        dbc.Button([
                            html.I(className="bi bi-graph-up-arrow me-2"),
                            "Generate Graphs"
                        ], id="generate-graph-btn", disabled=is_disabled, color="primary", class_name="w-100"),
                    ], width=3, md=3)
                ])
            ], class_name="shadow-sm mb-4"),
        ]),
        dbc.Alert(
            id="graph-alert",
            is_open=False,
            dismissable=True,
            color=None,
            fade=True,
        ),
        html.Br(),
        html.Div(id="graph-content"),
    ]


@dash.callback(
    Output("generate-graph-btn", "disabled"),
    Input("model-selector", "value"),
    prevent_initial_call=True,
)
def button_disabled(model: str | None) -> bool:
    return False if model else True


@dash.callback(
    [
        Output("graph-content", "children"),
        Output("graph-alert", "is_open"),
        Output("graph-alert", "children"),
        Output("graph-alert", "color"),
    ],
    Input("generate-graph-btn", "n_clicks"),
    [
        State("model-selector", "value"),
        State("global-timezone", "data"),
    ],
    prevent_initial_call=True
)
def update_graphs(n_clicks: int, model: str | None, timezone: str) -> tuple[Component, bool, list[dbc.Row], str]:
    if not n_clicks or not model:
        return (no_update, ) * 4

    ds = DataServices()

    valid_models = ds.get_model()
    if model not in valid_models:
        return no_update, True, format_alert_content(title="Error", content="Not a valid model."), "danger"

    try:
        raw_data = ds.get_battery_data("analysis_results", model=model)
        viz = Visualizer()

        trend_graph = viz.gen_battery_changing_chart(data=raw_data, model=model, timezone=timezone)
        health_graph = viz.gen_battery_health_chart(data=raw_data, model=model, timezone=timezone)

        graphs_layout = dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Capacity History Trend"),
                    dbc.CardBody(dcc.Graph(figure=trend_graph, responsive=True, style={"height": "625px"})),
                ], class_name="shadow-sm mb-4 h-100"),
            ], width=12, lg=7),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Battery Health Overview"),
                    dbc.CardBody(dcc.Graph(figure=health_graph, responsive=True, style={"height": "625px"})),
                ], class_name="shadow-sm mb-4 h-100"),
            ], width=12, lg=5),
        ], justify="center")

        return graphs_layout, False, no_update, no_update
    except Exception as e:
        return no_update, True, format_alert_content(title="Error", content=f"Visualization Error: {str(e)}"), "danger"

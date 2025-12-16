from datetime import datetime

import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, ctx, ALL, no_update
from dash.development.base_component import Component

from components import ThreadMode
from src import UPLOAD_PATH
from utils import format_alert_content

dash.register_page(__name__, path="/processing", order=3)


def get_table_body() -> list[html.Tr]:
    if not UPLOAD_PATH.exists():
        return [html.Tr([html.Td("Upload directory not found.", colSpan=5, className="text-center")])]

    zips = list(UPLOAD_PATH.glob("*.zip"))
    zips.sort(key=lambda f: f.stat().st_mtime, reverse=True)

    if not zips:
        return [html.Tr([html.Td([
            "No zip files found. Please click ",
            dcc.Link("here", href="/uploads"),
            " to upload first."
        ], colSpan=5, className="text-center text-muted")])]

    rows = []
    for i, filepath in enumerate(zips, start=1):
        stat = filepath.stat()
        file_size_mb = stat.st_size / (1024 ** 2)
        mod_time = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")

        delete_btn = dbc.Button(
            html.I(className="bi bi-trash"),
            id={"type": "file-delete-btn", "index": filepath.name},
            color="danger",
            size="sm",
            outline=True,
            title="Delete this file",
        )

        rows.append(html.Tr([
            html.Td(i),
            html.Td(filepath.name, className="fw-bold"),
            html.Td(f"{file_size_mb:.2f} MB"),
            html.Td(mod_time),
            html.Td(delete_btn, className="text-center")
        ]))

    return rows


def layout() -> list[Component]:
    return [
        dbc.Card([
            dbc.CardHeader(html.H5("Control Panel", className="m-0")),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Operation Mode", class_name="fw-bold"),
                        dbc.Select(
                            id="operation-mode-selector",
                            options=[
                                {"label": "Initialize (Clear DB & Start New)", "value": "init"},
                                {"label": "Append (Add to Existing DB)", "value": "append"}
                            ],
                            value="init"
                        )
                    ], width=12, md=6),
                    dbc.Col([
                        dbc.Label("Processing Performance Mode", class_name="fw-bold"),
                        dbc.Select(
                            id="thread-mode-selector",
                            options=[
                                {"label": "Low (Conservative)", "value": ThreadMode.LOW},
                                {"label": "Medium (Recommended)", "value": ThreadMode.MEDIUM},
                                {"label": "High (Maximum Performance)", "value": ThreadMode.HIGH}
                            ],
                            value=ThreadMode.MEDIUM,
                            class_name="mb-3"
                        )
                    ], width=12, md=6),
                ]),
                dbc.Row([
                    dbc.Col(
                        dbc.Button([
                            html.I(className="bi bi-play-circle me-2"),
                            "Start Processing"
                        ], id="start-process-btn", color="primary", class_name="w-100 fw-bold mt-2"),
                        width=3,
                    )
                ]),
                html.Br(),
                dbc.Row([
                    dbc.Col(
                        dbc.Alert(
                            id="process-alert",
                            children=[],
                            color=None,
                            is_open=False,
                            dismissable=True,
                            fade=True
                        ),
                        width=12,
                    )
                ])
            ]),
        ], class_name="shadow-sm"),
        html.Br(),
        dbc.Card([
            dbc.CardHeader(
                html.Div([
                    html.H5("File Manager", className="m-0 d-inline-block"),
                    dbc.Badge("Auto-Scanning", color="info", class_name="ms-2", text_color="white"),
                ]),
            ),
            dbc.CardBody(
                dbc.Table([
                    html.Thead(html.Tr([
                        html.Th("#", style={"width": "5%"}),
                        html.Th("Filename", style={"width": "40%"}),
                        html.Th("Size", style={"width": "15%"}),
                        html.Th("Uploaded Time", style={"width": "25%"}),
                        html.Th("Operations", className="text-center", style={"width": "15%"})
                    ])),
                    html.Tbody(get_table_body(), id="file-list-body")
                ], bordered=True, hover=True, responsive=True, striped=True, class_name="mb-0 align-middle")
            ),
        ], class_name="shadow-sm")
    ]


@dash.callback(
    [
        Output("file-list-body", "children"),
        Output("process-alert", "is_open"),
        Output("process-alert", "children"),
        Output("process-alert", "color")
    ],
    Input({"type": "file-delete-btn", "index": ALL}, "n_clicks"),
    prevent_initial_call=True
)
def file_deletion_handler(_) -> tuple[list[Component], bool, list[dbc.Row], str]:
    triggered = ctx.triggered_id
    if not triggered or not (filename := triggered["index"]):
        return (no_update,) * 4

    target = UPLOAD_PATH / filename
    try:
        if target.exists():
            target.unlink()
    except OSError:
        pass

    return get_table_body(), True, format_alert_content(title="Success",
                                                        content=f"Deleted file '{filename}'."), "success"

from datetime import datetime
from typing import Literal, Callable

import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State, ctx, ALL, no_update
from dash.development.base_component import Component

from components import ThreadMode
from src import UPLOAD_PATH
from utils import format_alert_content, analysis_pipeline

dash.register_page(__name__, path="/processing", order=3)


def get_store() -> list[dcc.Store]:
    return [
        dcc.Store(id="deletion-target-file", data=None),
    ]


def get_deletion_modal() -> dbc.Modal:
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Confirm Deletion")),
        dbc.ModalBody(id="deletion-modal-body"),
        dbc.ModalFooter([
            dbc.Button("Cancel", id="deletion-modal-close-btn", class_name="ms-auto", n_clicks=0),
            dbc.Button("Delete", id="deletion-modal-delete-btn", color="danger", class_name="ms-2", n_clicks=0),
        ]),
    ], id="deletion-modal", is_open=False, backdrop="static")


def get_table_body() -> list[html.Tr]:
    if not UPLOAD_PATH.exists():
        UPLOAD_PATH.mkdir(parents=True, exist_ok=True)

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
        get_deletion_modal(),
        *get_store(),
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
                        dbc.Collapse(
                            html.Div([
                                dbc.Progress(id="progress", value=0, striped=True, animated=True, class_name="mb-2"),
                                html.Div(id="status-text", className="text-muted small text-center"),
                            ]),
                            id="progress-collapse",
                            is_open=False,
                        ),
                        width=12,
                    ),
                ]),
                html.Br(),
                dbc.Row([
                    dbc.Col(
                        dbc.Alert(
                            id="alert",
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
                    html.H5("File List", className="m-0 d-inline-block"),
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
        Output("deletion-modal", "is_open"),
        Output("deletion-modal-body", "children"),
        Output("deletion-target-file", "data")
    ],
    [
        Input({"type": "file-delete-btn", "index": ALL}, "n_clicks"),
        Input("deletion-modal-close-btn", "n_clicks"),
        Input("deletion-modal-delete-btn", "n_clicks"),
    ],
    prevent_initial_call=True
)
def toggle_deletion_modal(_1, _2, _3) -> tuple[bool, html.Div, str]:
    triggered = ctx.triggered_id

    # if user click the deletion icon in file list
    if isinstance(triggered, dict) and triggered.get("type") == "file-delete-btn":
        filename = triggered["index"]
        modal_content = html.Div([
            html.P("Are you sure you want to delete this file?", className="mb-2"),
            html.Strong(filename, className="text-danger user-select-all"),
            html.P("This action cannot be undone.", className="text-muted small mt-2")
        ])
        return True, modal_content, filename

    if triggered in ["deletion-modal-close-btn", "deletion-modal-delete-btn"]:
        return False, no_update, no_update

    return (no_update, ) * 3


@dash.callback(
    [
        Output("file-list-body", "children"),
        Output("alert", "is_open", allow_duplicate=True),
        Output("alert", "children", allow_duplicate=True),
        Output("alert", "color", allow_duplicate=True)
    ],
    Input("deletion-modal-delete-btn", "n_clicks"),
    State("deletion-target-file", "data"),
    prevent_initial_call=True
)
def confirm_deletion(n_clicks: int, filename: str):
    if not n_clicks or not filename:
        return (no_update, ) * 4

    target = UPLOAD_PATH / filename

    try:
        if target.exists():
            target.unlink()
    except OSError:
        pass

    return (
        get_table_body(),
        True,
        format_alert_content(title="File Deleted", content=f"Successfully deleted '{filename}'."),
        "success"
    )


@dash.callback(
    [
        Output("alert", "is_open", allow_duplicate=True),
        Output("alert", "children", allow_duplicate=True),
        Output("alert", "color", allow_duplicate=True),
        Output("progress-collapse", "is_open"),
    ],
    Input("start-process-btn", "n_clicks"),
    [
        State("operation-mode-selector", "value"),
        State("thread-mode-selector", "value"),
    ],
    background=True,
    running=[
        (Output("start-process-btn", "disabled"), True, False),
        (Output("operation-mode-selector", "disabled"), True, False),
        (Output("thread-mode-selector", "disabled"), True, False),
        (Output("progress-collapse", "is_open"), True, False),
        (Output("status-text", "children"), "Initializing...", ""),
    ],
    progress=[
        Output("progress", "value"),
        Output("status-text", "children"),
    ],
    prevent_initial_call=True,
)
def decompress_handler(
        set_progress: Callable,
        _,
        opt_mode: Literal["init", "append"],
        thread: Literal["low", "medium", "high"]
) -> tuple[bool, list[dbc.Row], str, bool]:
    try:
        results = analysis_pipeline(mode=opt_mode, thread=thread, set_progress=set_progress)

        if results["status"] == "success":
            return True, format_alert_content("Analysis Complete", results["message"]), "success", False
        else:
            return True, format_alert_content("Analysis Failed", results["message"]), "danger", False

    except Exception as e:
        return True, format_alert_content("Critical Error", f"An unexpected error occurred: {str(e)}"), "danger", False
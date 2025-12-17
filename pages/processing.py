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
        dcc.Store(id="deletion-target-file", data=[]),
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
        ], colSpan=6, className="text-center text-muted")])]

    rows = []
    for i, filepath in enumerate(zips, start=1):
        stat = filepath.stat()
        file_size_mb = stat.st_size / (1024 ** 2)
        mod_time = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")

        checkbox = dbc.Checkbox(
            id={"type": "file-checkbox", "index": filepath.name},
            value=False,
            class_name="align-middle",
        )

        delete_btn = dbc.Button(
            html.I(className="bi bi-trash"),
            id={"type": "file-delete-btn", "index": filepath.name},
            color="danger",
            size="sm",
            outline=True,
            title="Delete this file",
        )

        rows.append(html.Tr([
            html.Td(checkbox, className="text-center"),
            html.Td(i),
            html.Td(filepath.name, className="fw-bold"),
            html.Td(f"{file_size_mb:.2f} MB"),
            html.Td(mod_time),
            html.Td(delete_btn, className="text-center")
        ]))

    return rows


def layout() -> list[Component]:
    has_file = False
    if UPLOAD_PATH.exists():
        has_file = any(UPLOAD_PATH.glob("*.zip"))

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
                    ),
                    dbc.Col(
                        dbc.Button([
                            html.I(className="bi bi-trash3-fill me-2"),
                            "Delete Selected"
                        ], id="bulk-delete-btn", color="danger", outline=False, class_name="w-100 fw-bold mt-2"),
                        width=3,
                    ),
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
                        html.Th(
                            dbc.Checkbox(
                                id="select-all-checkbox",
                                value=False,
                                disabled=not has_file,
                                class_name="text-center",
                            ),
                            className="text-center",
                        ),
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


dash.clientside_callback(
    """
    (selectAll, rowValues) => {
        const ctx = dash_clientside.callback_context;
        if (!ctx.triggered || ctx.triggered.length === 0) {
            return [window.dash_clientside.no_update, window.dash_clientside.no_update];
        }
        
        const triggerId = ctx.triggered[0].prop_id;
        if (triggerId === "select-all-checkbox.value") {
            return [selectAll, Array(rowValues.length).fill(selectAll)];
        }
        
        const allChecked = rowValues.every(Boolean);
        return [allChecked, window.dash_clientside.no_update];
    }
    """,
    [
        Output("select-all-checkbox", "value", allow_duplicate=True),
        Output({"type": "file-checkbox", "index": ALL}, "value"),
    ],
    [
        Input("select-all-checkbox", "value"),
        Input({"type": "file-checkbox", "index": ALL}, "value"),
    ],
    prevent_initial_call=True
)


@dash.callback(
    [
        Output("deletion-modal", "is_open"),
        Output("deletion-modal-body", "children"),
        Output("deletion-target-file", "data"),

        # Used only to warn users that no file has been selected
        Output("alert", "is_open", allow_duplicate=True),
        Output("alert", "children", allow_duplicate=True),
        Output("alert", "color", allow_duplicate=True),
    ],
    [
        Input({"type": "file-delete-btn", "index": ALL}, "n_clicks"),
        Input("bulk-delete-btn", "n_clicks"),
        Input("deletion-modal-close-btn", "n_clicks"),
        Input("deletion-modal-delete-btn", "n_clicks"),
    ],
    [
        State({"type": "file-checkbox", "index": ALL}, "value"),
        State({"type": "file-checkbox", "index": ALL}, "id"),
    ],
    prevent_initial_call=True
)
def toggle_deletion_modal(
        _1, _2, _3, _4,
        checkbox_values: list[bool],
        checkbox_ids: list[dict[str, str]],
) -> tuple[bool, html.Div, list[str], bool, list[dbc.Row], str]:
    triggered = ctx.triggered_id

    if triggered in ["deletion-modal-close-btn", "deletion-modal-delete-btn"]:
        return False, no_update, no_update, no_update, no_update, no_update

    # if user click the deletion icon in file list
    if isinstance(triggered, dict) and triggered.get("type") == "file-delete-btn":
        filename = triggered["index"]
        modal_content = html.Div([
            html.P("Are you sure you want to delete this file?", className="mb-2"),
            html.Strong(filename, className="user-select-all"),
            html.P("This action cannot be undone.", className="text-danger small mt-2")
        ])
        return True, modal_content, [filename], False, no_update, no_update

    # if user select checkbox and click the bulk delect button
    if triggered == "bulk-delete-btn":
        selected_files = [id_obj["index"] for val, id_obj in zip(checkbox_values, checkbox_ids) if val]
        if not selected_files:
            return False, no_update, no_update, True, format_alert_content(title="Error", content="Please select at least 1 file to delete."), "danger"

        count = len(selected_files)
        display_limit = 10
        list_items = [html.Li(f) for f in selected_files[:display_limit]]

        summary_text = f"Total: {count} files"
        if count > display_limit:
            remaining = count - display_limit
            summary_text = f"...and {remaining} more files ({summary_text})."

        modal_content = html.Div([
            html.P("Are you sure you want to delete the following files?", className="mb-2"),
            html.Ul(list_items, className="small text-muted p-2"),
            html.P(summary_text),
            html.P("WARNING", className="text-danger fw-bold"),
            html.P("This action cannot be undone.", className="text-danger fw-bold mt-2")
        ])
        return True, modal_content, selected_files, False, no_update, no_update

    return (no_update, ) * 6


@dash.callback(
    [
        Output("file-list-body", "children"),
        Output("alert", "is_open", allow_duplicate=True),
        Output("alert", "children", allow_duplicate=True),
        Output("alert", "color", allow_duplicate=True),
        Output("select-all-checkbox", "disabled"),
        Output("select-all-checkbox", "value", allow_duplicate=True),
    ],
    Input("deletion-modal-delete-btn", "n_clicks"),
    State("deletion-target-file", "data"),
    prevent_initial_call=True
)
def confirm_deletion(
        n_clicks: int,
        filenames: list
) -> tuple[list[html.Tr], bool, list[dbc.Row], str, bool, bool]:
    if not n_clicks or not filenames:
        return (no_update, ) * 6

    deleted_count = 0
    errors = {}

    for name in filenames:
        target = UPLOAD_PATH / name

        try:
            if target.exists():
                target.unlink()
                deleted_count += 1
        except Exception as e:
            errors[name] = str(e)

    if errors:
        msg = [
            html.P(f"Deleted {deleted_count} files successfully."),
            html.P(f"Failed to delete {len(errors)} files:", className="fw-bold"),
            html.Ul([html.Li(f"Name: {i}, Error: {v}") for i, v in errors.items()])
        ]
        color = "warning"
    else:
        msg = f"Successfully deleted {deleted_count} files."
        color = "success"

    remaining_files = list(UPLOAD_PATH.glob("*.zip"))
    is_empty = len(remaining_files) == 0

    return (
        get_table_body(),
        True,
        format_alert_content(title="File Deleted", content=msg),
        color,
        is_empty,
        False
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
        (Output("bulk-delete-btn", "disabled"), True, False),
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
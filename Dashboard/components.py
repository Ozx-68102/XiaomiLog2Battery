from enum import StrEnum

import dash_bootstrap_components as dbc
import dash_uploader as du
from dash import dcc, html


class ProcessStatus(StrEnum):
    INIT = "init"
    SUCCESS = "success"
    ERROR = "error"


class ThreadCountMode(StrEnum):
    """Thread count performance mode enumeration"""
    LOW = "low"  # Low performance mode (conservative resource usage)
    BALANCED = "balanced"  # Balanced mode (recommended)
    HIGH = "high"  # High performance mode (maximum resource usage)


def create_stores() -> list[dcc.Store]:
    """
    Create all data storage components for the app.
    """
    return [
        # if upload completed, it will determine whether to proceed to the next step (parse)
        dcc.Store(id="upload-results", data={"status": ProcessStatus.INIT, "filepath": []}),
        dcc.Store(id="parse-trigger", data={"status": ProcessStatus.INIT}),
        # make sure that parsed-data is not empty
        dcc.Store(id="parsed-data", data={"status": ProcessStatus.INIT, "value": []}),
        dcc.Store(id="viz-trigger", data={"status": ProcessStatus.INIT}),
        dcc.Store(id="viz-res", data={"status": ProcessStatus.INIT}),
        # Store for data operation mode (init or add)
        dcc.Store(id="operation-mode", data="init"),
        # Store for thread count setting
        dcc.Store(id="thread-count", data=ThreadCountMode.BALANCED),
    ]


def create_header() -> dbc.Row:
    """
    Create the header of the app.
    """
    return dbc.Row(
        dbc.Col(html.H1("Xiaomi Battery Log Analyzer", className="text-center my-4"), width=12)
    )


def create_mode_info() -> dbc.Row:
    """
    Create the information about the operation mode and thread count settings.
    """
    return dbc.Row(
        dbc.Alert(
            [
                html.Div([
                    html.Div("Operation Mode:", className="fw-bold"),
                    html.Ul([
                        html.Li("Initialize mode: Clear the existing database and recreate it."),
                        html.Li("Add mode: Preserve existing data and append new data.")
                    ])
                ], className="mb-3"),
                html.Div([
                    html.Div("Processing Performance Mode:", className="fw-bold"),
                    html.Ul([
                        html.Li([
                            html.Strong("Low Mode: "),
                            "Conservative resource usage. Suitable for systems with limited resources or when you need to keep the system responsive."
                        ]),
                        html.Li([
                            html.Strong("Balanced Mode (Recommended): "),
                            "Optimal balance between processing speed and system resource usage. Best for most users."
                        ]),
                        html.Li([
                            html.Strong("High Mode: "),
                            "Maximum performance mode.",
                            html.Br(),
                            html.Strong("Warning: ", className="text-warning"),
                            "This mode will maximize system resource usage and may cause system lag or freezing, especially on systems with limited CPU cores or memory."
                        ], className="text-warning")
                    ])
                ])
            ],
            color="info",
            dismissable=False,
            className="mb-3"
        )
    )


def create_mode_selector() -> dbc.Col:
    """
    Create the dropdown menu for the operation mode.
    """
    return dbc.Col([
        dbc.Label("Select Operation Mode:", className="mb-2"),
        dcc.Dropdown(
            id="mode-dropdown",
            options=[
                {"label": "Initialize Database (Overwrite Existing Data)", "value": "init"},
                {"label": "Append to Existing Database", "value": "add"}
            ],
            value="init",
            clearable=False,
            searchable=False,
            className="mb-4",
            disabled=False  # Will be controlled by callback
        )
    ], width=6, className="user-select-none")


def create_thread_count_selector() -> dbc.Col:
    """
    Create the dropdown menu for processing performance mode selection.
    """
    options = [
        {"label": "Low Mode (Conservative)", "value": ThreadCountMode.LOW},
        {"label": "Balanced Mode (Recommended)", "value": ThreadCountMode.BALANCED},
        {"label": "High Mode (Maximum Performance)", "value": ThreadCountMode.HIGH}
    ]

    return dbc.Col([
        dbc.Label("Processing Performance Mode:", className="mb-2"),
        dcc.Dropdown(
            id="thread-count-dropdown",
            options=options,
            value=ThreadCountMode.BALANCED,  # Default to balanced
            clearable=False,
            searchable=False,
            className="mb-4",
            disabled=False  # Will be controlled by callback
        )
    ], width=6, className="user-select-none")


def create_settings_row() -> dbc.Row:
    """
    Create a row containing both mode selector and thread count selector.
    """
    return dbc.Row([
        create_mode_selector(),
        create_thread_count_selector()
    ], className="mb-4")


def create_upload_component(
        max_files: int,
        filetype: list[str] | None = None,
        complete_message: str = "Uploaded: ",
        only_show_message: bool = False,
        upload_id: str = "upload",
) -> dbc.Row:
    """
    Create the upload component for the app.
    """
    return dbc.Row(
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    du.Upload(
                        id="upload-component",
                        text=f"Drag files to here, or click it to select file(s). After that file(s) will be automatically uploaded. No more than {max_files} files.",
                        text_completed=complete_message,
                        text_completed_no_suffix=only_show_message,
                        max_files=max_files,
                        filetypes=filetype,
                        upload_id=upload_id,
                        is_uploading=False,
                        default_style={
                            "width": "100%",
                            "height": "100%",
                            "textAlign": "center",
                            "cursor": "pointer"
                        }
                    )
                ])
            ], style={
                "border": "1px dashed #007bff",
                "borderRadius": "8px",
                "background-color": "#f8f9fa"
            }, className="p-3")
        ], width=12),
        className="mb-4"
    )


def create_status_zones() -> list[dbc.Row]:
    """
    Create the status display zones for the app.
    """
    return [
        dbc.Row(html.Div(id="upload-status")),
        dbc.Row(html.Div(id="parse-status")),
        dbc.Row(html.Div(id="viz-status"))
    ]


def create_graph_zone() -> dbc.Row:
    """
    Create the graph display zone for the app.
    """
    return dbc.Row(
        html.Div(id="graph-zone", style={"display": "flex", "flexDirection": "column", "gap": "10px"})
    )

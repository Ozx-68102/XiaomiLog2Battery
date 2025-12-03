from enum import StrEnum

import dash_bootstrap_components as dbc
import dash_uploader as du
from dash import dcc, html


class ProcessStatus(StrEnum):
    INIT = "init"
    SUCCESS = "success"
    ERROR = "error"


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
    Create the information about the operation mode.
    """
    return dbc.Row(
        dbc.Alert(
            [
                html.Div("Operation Mode Description:", className="fw-bold"),
                html.Div(
                    "Initialize mode will clear the existing database and recreate it, and Add mode will preserve existing data and add new data."),
            ],
            color="info",
            dismissable=False,
            className="mb-3"
        )
    )


def create_mode_selector() -> dbc.Row:
    """
    Create the dropdown menu for the operation mode.
    """
    return dbc.Row(
        dbc.Col([
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
        ], width=6, className="mx-auto user-select-none")
    )


def create_upload_component(
        max_files: int,
        filetype: list[str] | None = None,
        complete_message: str = "Uploaded: ",
        only_message: bool = False,
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
                        text_completed_no_suffix=only_message,
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

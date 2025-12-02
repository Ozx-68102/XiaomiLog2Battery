import os
from enum import StrEnum

import dash
import dash_bootstrap_components as dbc
import dash_uploader as du
from dash import dcc, html, Output, Input, State, no_update, NoUpdate

from Modules.Core import parse_files, store_data, viz_battery_data
from Modules.FileProcess import INSTANCE_PATH
from .utils import format_status_prompt, upload_status_prompt

__MAX_FILES = 40


class ProcessStatus(StrEnum):
    INIT = "init"
    SUCCESS = "success"
    ERROR = "error"

basepath = os.path.dirname(os.path.abspath(__file__))
app = dash.Dash(__name__, assets_folder=os.path.join(basepath, "assets"))
app.config.suppress_callback_exceptions = True

du.configure_upload(app=app, folder=INSTANCE_PATH)

app.layout = dbc.Container([
    # if upload completed, it will determine whether to proceed to the next step (parse)
    dcc.Store(id="upload-results", data={"status": ProcessStatus.INIT, "filepath": []}),
    dcc.Store(id="parse-trigger", data={"status": ProcessStatus.INIT}),

    # make sure that parsed-data is not empty
    dcc.Store(id="parsed-data", data={"status": ProcessStatus.INIT, "value": []}),
    dcc.Store(id="viz-trigger", data={"status": ProcessStatus.INIT}),

    dcc.Store(id="viz-res", data={"status": ProcessStatus.INIT}),

    # Store for data operation mode (init or add)
    dcc.Store(id="operation-mode", data="init"),

    dbc.Row(
        dbc.Col(html.H1("Xiaomi Battery Log Analyzer", className="text-center my-4"), width=12)
    ),
    dbc.Row(
        dbc.Alert(
            [
                html.Div("Operation Mode Description:", className="fw-bold"),
                html.Div("Initialize mode will clear the existing database and recreate it, and Add mode will preserve existing data and add new data."),
            ],color="info", dismissable=False, className="mb-3"
        )
    ),

    # Add dropdown menu for operation mode selection
    dbc.Row(
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
    ),
    dbc.Row(
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    du.Upload(
                        id="upload-component",
                        text=f"Drag files to here, or click it to select file(s). After that file(s) will be automatically uploaded. No more than {__MAX_FILES} files.",
                        text_completed="Upload Accomplished !",
                        text_completed_no_suffix=True,
                        max_files=__MAX_FILES,
                        filetypes=[".zip"],
                        upload_id="upload",
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
        ], width=12), className="mb-4"
    ),
    dbc.Row(html.Div(id="upload-status")),
    dbc.Row(html.Div(id="parse-status")),
    dbc.Row(html.Div(id="viz-status")),
    dbc.Row(html.Div(id="graph-zone", style={"display": "flex", "flexDirection": "column", "gap": "10px"}))
], fluid=True, style={"padding": "15px"})


@app.callback(
    [
        Output(component_id="mode-dropdown", component_property="disabled"),
        Output(component_id="upload-component", component_property="disabled")
    ],
    [
        Input(component_id="upload-component", component_property="isUploading"),
        Input(component_id="upload-results", component_property="data"),
        Input(component_id="parsed-data", component_property="data"),
        Input(component_id="viz-trigger", component_property="data"),
        Input(component_id="viz-res", component_property="data")
    ],
    prevent_initial_call=True
)
def manage_interaction_state(
        is_uploading: bool,
        upload_res: dict[str, str | bool | list[str]],
        parsed_data: dict[str, str | list[str]],
        viz_trigger: dict[str, str],
        viz_res: dict[str, str]
) -> tuple[bool, bool]:
    is_processing = False   # `True` when upload finished but other process not yet

    # if upload finished...
    if upload_res.get("status", ProcessStatus.INIT) == ProcessStatus.SUCCESS:
        is_processing = True

        pipeline_states = [parsed_data, viz_trigger, viz_res]
        if any(state.get("status", ProcessStatus.INIT) == ProcessStatus.ERROR for state in pipeline_states):
            is_processing = False

        if viz_res.get("status", ProcessStatus.INIT) == ProcessStatus.SUCCESS:
            is_processing = False

    dropdown_disabled = is_uploading or is_processing
    uploader_disabled = is_processing

    return dropdown_disabled, uploader_disabled

@app.callback(
    Output(component_id="operation-mode", component_property="data"),
    Input(component_id="mode-dropdown", component_property="value")
)
def update_operation_mode(selected_mode: str) -> str:
    """
    Update the operation mode store based on dropdown selection.
    """
    return selected_mode


@app.callback(
    [
        # reset status
        Output(component_id="upload-results", component_property="data", allow_duplicate=True),
        Output(component_id="parse-trigger", component_property="data", allow_duplicate=True),
        Output(component_id="parsed-data", component_property="data", allow_duplicate=True),
        Output(component_id="viz-trigger", component_property="data", allow_duplicate=True),
        Output(component_id="viz-res", component_property="data", allow_duplicate=True),

        # reset UI
        Output(component_id="upload-status", component_property="children", allow_duplicate=True),
        Output(component_id="parse-status", component_property="children", allow_duplicate=True),
        Output(component_id="viz-status", component_property="children", allow_duplicate=True)
    ],
    Input(component_id="upload-component", component_property="isUploading"),
    prevent_initial_call=True
)
def on_upload_start(
        is_uploading: bool
) -> tuple[
    dict[str, str | list[str]] | NoUpdate,
    dict[str, str] | NoUpdate,
    dict[str, str | list[str]] | NoUpdate,
    dict[str, str] | NoUpdate,
    dict[str, str] | NoUpdate,
    dbc.Alert | NoUpdate,
    html.Div | NoUpdate,
    html.Div | NoUpdate
]:
    if is_uploading:
        reset_data = {"status": ProcessStatus.INIT}
        reset_parsed_data = {"status": ProcessStatus.INIT, "value": []}
        reset_upload = {"status": ProcessStatus.INIT, "filepath": []}

        upload_prompt = format_status_prompt(
            title="Uploading...",
            msg=[html.P("Now files are uploading. It may take some time, so hang tight...")],
            color="info", dismissable=False
        )

        empty_ui = html.Div()

        return reset_upload, reset_data, reset_parsed_data, reset_data, reset_data, upload_prompt, empty_ui, empty_ui

    return (no_update, ) * 8

@du.callback(
    output=[
        Output(component_id="upload-status", component_property="children"),
        Output(component_id="upload-results", component_property="data")
    ],
    id="upload-component"
)
def on_uploading(status: du.UploadStatus) -> tuple[dbc.Alert, dict[str, str | list[str]]]:
    filepaths = [os.fspath(fp) for fp in status.uploaded_files]
    failed_files = status.failed_files if hasattr(status, "failed_files") else []

    if not status.is_completed:
        status_message, color = upload_status_prompt(success=filepaths, failed=failed_files, complete=False)
        status_display = format_status_prompt(title="Uploading...", msg=status_message, color=color, dismissable=False)

        return status_display, {"status": ProcessStatus.INIT, "filepath": []}

    status_message, color = upload_status_prompt(success=filepaths, failed=failed_files, complete=True)
    status_display = format_status_prompt(title="Upload Completed", msg=status_message, color=color, dismissable=True)

    success_count = len(filepaths)

    proc_status = ProcessStatus.SUCCESS if success_count > 0 else ProcessStatus.ERROR
    dcc_store_data = {"status": proc_status, "filepath": filepaths}

    return status_display, dcc_store_data


@app.callback(
    [
        Output(component_id="parse-status", component_property="children", allow_duplicate=True),
        Output(component_id="parse-trigger", component_property="data")
    ],
    Input(component_id="upload-results", component_property="data"),
    prevent_initial_call=True
)
def parse_trigger(
        upload_res: dict[str, str | bool | list[str]]
) -> tuple[html.Div | dbc.Alert | NoUpdate, dict[str, str] | NoUpdate]:
    if upload_res.get("status", ProcessStatus.INIT) != ProcessStatus.SUCCESS:
        return no_update, no_update

    total_files = len(upload_res.get("filepath", []))
    message = [html.P(f"Parsing and storing data (Total: {total_files}) now. It may take some time. Hang tight...")]
    status_display = format_status_prompt(title="Parsing Data", msg=message, color="info", dismissable=False)

    return status_display, {"status": ProcessStatus.SUCCESS}


@app.callback(
    Output(component_id="parsed-data", component_property="data"),
    Input(component_id="parse-trigger", component_property="data"),
    State(component_id="upload-results", component_property="data")
)
def parse_handler(
        parsed_data: dict[str, str | list[str]], upload_res: dict[str, str | bool | list[str]]
) -> dict[str, str | list[dict[str, str | int]]] | NoUpdate:
    if parsed_data.get("status", ProcessStatus.INIT) != ProcessStatus.SUCCESS:
        return no_update

    parsed_data = parse_files(filepath_list=upload_res.get("filepath", []))
    return {"status": ProcessStatus.SUCCESS, "value": parsed_data}


@app.callback(
    [
        Output(component_id="parse-status", component_property="children", allow_duplicate=True),
        Output(component_id="viz-trigger", component_property="data")
    ],
    Input(component_id="parsed-data", component_property="data"),
    State(component_id="operation-mode", component_property="data"),
    prevent_initial_call=True
)
def store_handler(
        data: dict[str, str | list[dict[str, str | int]]],
        operation_mode: str
) -> tuple[dbc.Alert | html.Div | NoUpdate, dict[str, str] | NoUpdate]:
    if data.get("status", ProcessStatus.INIT) == ProcessStatus.INIT:
        return no_update, no_update

    if data.get("status", ProcessStatus.INIT) == ProcessStatus.ERROR:
        return format_status_prompt(
            title="Failed to parse data", msg=[html.P("No valid data found.")], color="danger", dismissable=True
        ), {"status": ProcessStatus.ERROR}

    parsed_data = data.get("value", [])
    if not parsed_data:
        return format_status_prompt(
            title="No Data Found",
            msg=[html.P("Files were processed but no battery logs were found or files were invalid.")],
            color="danger", dismissable=True
        ), {"status": ProcessStatus.ERROR}

    try:
        result = store_data(data=parsed_data, mode=operation_mode)
        if not result:
            return format_status_prompt(
                title="Failed to store data", msg=[html.P("Database error.")], color="danger", dismissable=True
            ), {"status": ProcessStatus.ERROR}
    except Exception as e:
        return format_status_prompt(
            title="Database Error", msg=[html.P(f"Error: {str(e)}")], color="danger", dismissable=True
        ), {"status": ProcessStatus.ERROR}

    msg = "Database initialized." if operation_mode == "init" else "Data appended."
    return format_status_prompt(
        title="Success for Parsing and Storing data", msg=[html.P(msg)], color="success", dismissable=True
    ), {"status": ProcessStatus.SUCCESS}


@app.callback(
    [
        Output(component_id="viz-status", component_property="children"),
        Output(component_id="viz-res", component_property="data"),
        Output(component_id="graph-zone", component_property="children")
    ],
    Input(component_id="viz-trigger", component_property="data"),
    prevent_initial_call=True
)
def viz_handler(trigger: dict[str, str]) -> tuple[dbc.Alert | html.Div | NoUpdate, dict[str, str] | NoUpdate, html.Div | NoUpdate]:
    status = trigger.get("status", ProcessStatus.INIT)
    if status == ProcessStatus.INIT or status == ProcessStatus.ERROR:
        return no_update, no_update, no_update

    graph, num = viz_battery_data()
    if graph is None:
        return format_status_prompt(
            title="Generate Error", msg=[html.P("Visualization failed.")], color="danger",dismissable=True
        ), {"status": ProcessStatus.ERROR}, html.Div()

    return format_status_prompt(
        title="Visualize Success", msg=[html.P(f"{num} graph(s) generated.")], color="success", dismissable=True
    ), {"status": ProcessStatus.SUCCESS}, graph


if __name__ == "__main__":
    pass

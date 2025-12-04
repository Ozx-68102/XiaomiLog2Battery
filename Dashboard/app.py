import os
from typing import Literal

import dash
import dash_bootstrap_components as dbc
import dash_uploader as du
from dash import html, Output, Input, State, no_update, NoUpdate

from Dashboard import components, utils
from Modules.Core import parse_files, store_data, viz_battery_data, get_max_cycle_count, clear_upload_folder
from Modules.FileProcess import INSTANCE_PATH

__UPLOAD_FOLDER = "upload"

basepath = os.path.dirname(os.path.abspath(__file__))
app = dash.Dash(__name__, assets_folder=os.path.join(basepath, "assets"))
app.config.suppress_callback_exceptions = True

du.configure_upload(app=app, folder=INSTANCE_PATH)

app.layout = dbc.Container([
    *components.create_stores(),
    components.create_header(),
    components.create_mode_info(),
    components.create_settings_row(),
    components.create_upload_component(
        max_files=40,
        filetype=[".zip"],
        complete_message="Upload Accomplished! You can continue to upload by dragging files or clicking me",
        only_show_message=True,
        upload_id=__UPLOAD_FOLDER,
        max_size_mb=10 * 1024,
        chunk_size_mb=30    # protect the hard disk
    ),
    *components.create_status_zones(),
    components.create_cycle_count_alert(),
    components.create_graph_zone()
], fluid=True, style={"padding": "15px"})


@app.callback(
    [
        Output(component_id="mode-dropdown", component_property="disabled"),
        Output(component_id="thread-count-dropdown", component_property="disabled"),
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
) -> tuple[bool, bool, bool]:
    is_processing = False   # `True` when upload finished but other process not yet

    # if upload finished...
    if upload_res.get("status", components.ProcessStatus.INIT) == components.ProcessStatus.SUCCESS:
        is_processing = True

        pipeline_states = [parsed_data, viz_trigger, viz_res]
        if any(
                state.get("status", components.ProcessStatus.INIT) == components.ProcessStatus.ERROR
                for state in pipeline_states
        ):
            is_processing = False

        if viz_res.get("status", components.ProcessStatus.INIT) == components.ProcessStatus.SUCCESS:
            is_processing = False

    dropdown_disabled = is_uploading or is_processing
    uploader_disabled = is_processing

    return dropdown_disabled, dropdown_disabled, uploader_disabled

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
    Output(component_id="thread-count", component_property="data"),
    Input(component_id="thread-count-dropdown", component_property="value")
)
def update_thread_count(selected_count: str) -> str:
    """
    Update the thread count store based on dropdown selection.
    """
    return selected_count


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
    [
        Input(component_id="upload-component", component_property="isUploading"),
        Input(component_id="upload-component", component_property="isCancelled")
    ],
    prevent_initial_call=True
)
def on_upload_start(
        is_uploading: bool,
        is_cancelled: bool
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
    reset_data = {"status": components.ProcessStatus.INIT}
    reset_parsed_data = {"status": components.ProcessStatus.INIT, "value": []}
    reset_upload = {"status": components.ProcessStatus.INIT, "filepath": []}
    empty_ui = html.Div()
    prompt = None

    if is_uploading:
        clear_upload_folder(fp=os.path.join(INSTANCE_PATH, __UPLOAD_FOLDER))
        prompt = utils.format_status_prompt(
            title="Uploading...",
            msg=[html.P("Now files are uploading. It may take some time, so hang tight...")],
            color="info", dismissable=False
        )
    elif is_cancelled:
        prompt = utils.format_status_prompt(
            title="Upload Cancelled",
            msg=[html.P("File upload has been cancelled by user. All states have been reset.")],
            color="warning", dismissable=True
        )

    return (
        reset_upload, reset_data, reset_parsed_data, reset_data, reset_data, prompt, empty_ui, empty_ui
    ) if prompt else (no_update,) * 8


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
        status_message, color = utils.upload_status_prompt(success=filepaths, failed=failed_files, complete=False)
        status_display = utils.format_status_prompt(title="Uploading...", msg=status_message, color=color, dismissable=False)

        return status_display, {"status": components.ProcessStatus.INIT, "filepath": []}

    status_message, color = utils.upload_status_prompt(success=filepaths, failed=failed_files, complete=True)
    status_display = utils.format_status_prompt(title="Upload Completed", msg=status_message, color=color, dismissable=True)

    success_count = len(filepaths)

    proc_status = components.ProcessStatus.SUCCESS if success_count > 0 else components.ProcessStatus.ERROR
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
    if upload_res.get("status", components.ProcessStatus.INIT) != components.ProcessStatus.SUCCESS:
        return no_update, no_update

    total_files = len(upload_res.get("filepath", []))
    message = [html.P(f"Parsing and storing data (Total: {total_files}) now. It may take some time. Hang tight...")]
    status_display = utils.format_status_prompt(title="Parsing Data", msg=message, color="info", dismissable=False)

    return status_display, {"status": components.ProcessStatus.SUCCESS}


@app.callback(
    Output(component_id="parsed-data", component_property="data"),
    Input(component_id="parse-trigger", component_property="data"),
    State(component_id="upload-results", component_property="data"),
    State(component_id="thread-count", component_property="data")
)
def parse_handler(
        parsed_data: dict[str, str | list[str]],
        upload_res: dict[str, str | bool | list[str]],
        thread_count: Literal["low", "balanced", "high"]
) -> dict[str, str | list[dict[str, str | int]]] | NoUpdate:
    if parsed_data.get("status", components.ProcessStatus.INIT) != components.ProcessStatus.SUCCESS:
        return no_update

    # Pass the mode string directly to backend for calculation
    parsed_data = parse_files(filepath_list=upload_res.get("filepath", []), thread_count_mode=thread_count)
    return {"status": components.ProcessStatus.SUCCESS, "value": parsed_data}


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
    if data.get("status", components.ProcessStatus.INIT) == components.ProcessStatus.INIT:
        return no_update, no_update

    if data.get("status", components.ProcessStatus.INIT) == components.ProcessStatus.ERROR:
        return utils.format_status_prompt(
            title="Failed to parse data", msg=[html.P("No valid data found.")], color="danger", dismissable=True
        ), {"status": components.ProcessStatus.ERROR}

    parsed_data = data.get("value", [])
    if not parsed_data:
        return utils.format_status_prompt(
            title="No Data Found",
            msg=[html.P("Files were processed but no battery logs were found or files were invalid.")],
            color="danger", dismissable=True
        ), {"status": components.ProcessStatus.ERROR}

    try:
        result = store_data(data=parsed_data, mode=operation_mode)
        if result == 0:
            return utils.format_status_prompt(
                title="Failed to store data", msg=[html.P("Database error.")], color="danger", dismissable=True
            ), {"status": components.ProcessStatus.ERROR}
    except Exception as e:
        return utils.format_status_prompt(
            title="Database Error", msg=[html.P(f"Error: {str(e)}")], color="danger", dismissable=True
        ), {"status": components.ProcessStatus.ERROR}

    msg = "Database initialized." if operation_mode == "init" else "Data appended."
    return utils.format_status_prompt(
        title="Success for Parsing and Storing data", msg=[html.P(msg)], color="success", dismissable=True
    ), {"status": components.ProcessStatus.SUCCESS}


@app.callback(
    [
        Output(component_id="viz-status", component_property="children"),
        Output(component_id="viz-res", component_property="data"),
        Output(component_id="graph-zone", component_property="children"),
        Output(component_id="max-cycle-count", component_property="children"),
        Output(component_id="cycle-count-row", component_property="style")
    ],
    Input(component_id="viz-trigger", component_property="data"),
    prevent_initial_call=True
)
def viz_handler(
        trigger: dict[str, str]
) -> tuple[
    dbc.Alert | html.Div | NoUpdate,
    dict[str, str] | NoUpdate,
    html.Div | dbc.Container | NoUpdate,
    str | NoUpdate,
    dict[str, str] | NoUpdate
]:
    status = trigger.get("status", components.ProcessStatus.INIT)
    if status == components.ProcessStatus.INIT or status == components.ProcessStatus.ERROR:
        return (no_update, ) * 5

    try:
        graph, num = viz_battery_data()
        if graph is None:
            return utils.format_status_prompt(
                title="Generate Error", msg=[html.P("Visualization failed.")], color="danger",dismissable=True
            ), {"status": components.ProcessStatus.ERROR}, html.Div(), no_update, {"display": "none"}

        # Calculate max cycle count
        max_cycle_count = get_max_cycle_count()
        cycle_count_style = {"display": "block"} if max_cycle_count != "N/A" else {"display": "none"}

        return utils.format_status_prompt(
            title="Visualize Success", msg=[html.P(f"{num} graph(s) generated.")], color="success", dismissable=True
        ), {"status": components.ProcessStatus.SUCCESS}, graph, max_cycle_count, cycle_count_style
    except Exception as e:
        error_msg = f"Visualization failed: {str(e)}"
        print(f"Visualization Error: {e}")
        return utils.format_status_prompt(
            title="Visualization Error", msg=[html.P(error_msg)], color="danger", dismissable=True
        ), {"status": components.ProcessStatus.ERROR}, html.Div(), no_update, {"display": "none"}


if __name__ == "__main__":
    pass

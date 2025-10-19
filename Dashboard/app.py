import os

import dash
import dash_bootstrap_components as dbc
import dash_uploader as du
from dash import dcc, html, Output, Input, no_update, NoUpdate

from Modules.FileProcess import INSTANCE_PATH
from .utils import format_status_prompt, upload_status_prompt

basepath = os.path.dirname(os.path.abspath(__file__))

app = dash.Dash(__name__, assets_folder=os.path.join(basepath, "assets"))
app.config.suppress_callback_exceptions = True

du.configure_upload(app=app, folder=INSTANCE_PATH)

__UPLOAD_FAILED_FILES_LIST = []  # A place storing whole error files list

app.layout = dbc.Container([
    # Those 3 stores will be modified by `upload-prompt.js` => js code
    # It is all belongs to Upload procedure
    dcc.Store(
        id="js-update-prompt",
        data={
            "show": False, "title": None, "msg": None, "color": "info", "dismissable": None
        }
    ),
    dcc.Store(id="js-new-error-file", data={"filename": None}),  # Get a new error file
    dcc.Store(id="js-error-file-empty-trigger", data={"status": None}),  # clear the FAILED_FILES_LIST

    # if upload completed, it will determine whether to proceed to the next step (parse)
    dcc.Store(id="is-upload-completed", data={"status": False, "filepath": [], "all-failed": False}),
    dcc.Store(id="is-parse-begin", data={"status": False}),

    dbc.Row(
        dbc.Col(html.H1("Xiaomi Battery Log Analyzer", className="text-center my-4"), width=12)
    ),
    dbc.Row(
        dbc.Alert(
            "Kindly Note: For large files, upload may take some time. Please wait for confirmation.",
            color="info", dismissable=False, className="mb-3"
        )
    ),
    dbc.Row(
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    du.Upload(  # `filetypes` parameter does not work anymore
                        id="upload-component",
                        text="Drag files to here, or click it to select file(s). After that file(s) will be automatically uploaded. No more than 40 files.",
                        max_files=40,
                        upload_id="upload",
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
    ),
    dbc.Row(html.Div(id="upload-status")),
    dbc.Row(html.Div(id="parse-status")),
    dbc.Row(html.Div(id="output-container", style={"display": "flex", "flexDirection": "column", "gap": "10px"}))
], fluid=True, style={"padding": "15px"})


@app.callback(
    Output(component_id="js-error-file-empty-trigger", component_property="data"),
    Input(component_id="js-error-file-empty-trigger", component_property="data"),
    prevent_initial_call=True
)
def empty_error_list(data: dict[str, bool | None]) -> NoUpdate:
    """
    Use a variable to clear the global variable **__FAILED_FILES_LIST**.
    """
    global __UPLOAD_FAILED_FILES_LIST
    __UPLOAD_FAILED_FILES_LIST = []

    return no_update


@app.callback(
    Output(component_id="js-new-error-file", component_property="data"),
    Input(component_id="js-new-error-file", component_property="data"),
)
def add_new_error_file(data: dict[str, str]) -> NoUpdate:
    """
    Use a callback to add the error file to a global variable **__FAILED_FILES_LIST**.
    """
    global __UPLOAD_FAILED_FILES_LIST
    unique_list = set(__UPLOAD_FAILED_FILES_LIST)

    filename = data.get("filename", None)
    if filename and isinstance(filename, str):
        unique_list.add(filename)

    __UPLOAD_FAILED_FILES_LIST = list(unique_list)

    return no_update


@app.callback(
    Output(component_id="upload-status", component_property="children", allow_duplicate=True),
    Input(component_id="js-update-prompt", component_property="data"),
    prevent_initial_call=True
)
def render_upload_0t1_prompt(data: dict[str, str | bool]) -> dbc.Alert | html.Div:
    """
    Render a prompt when upload beginning, its message was operated by customized js file.
    """
    keywords = ["title", "msg", "color"]
    if data.get("show") and any((data.get(keyword) is not None) for keyword in keywords):
        return format_status_prompt(title=data.get("title"), msg=[data.get("msg")], color=data.get("color"))

    return html.Div()


@du.callback(
    output=[
        Output(component_id="upload-status", component_property="children"),
        Output(component_id="is-upload-completed", component_property="data")
    ],
    id="upload-component"
)
def upload_handler(status: du.UploadStatus) -> tuple[dbc.Alert, dict[str, bool | str]]:
    filepaths = [os.fspath(fp) for fp in status.uploaded_files]
    failed_files = __UPLOAD_FAILED_FILES_LIST

    if not status.is_completed:
        status_message, color = upload_status_prompt(success=filepaths, failed=failed_files, complete=False)
        status_display = format_status_prompt(title="Uploading...", msg=status_message, color=color, dismissable=False)

        return status_display, {"status": False, "filepath": [], "all-failed": False}

    status_message, color = upload_status_prompt(success=filepaths, failed=failed_files, complete=True)
    status_display = format_status_prompt(title="Upload Completed", msg=status_message, color=color, dismissable=True)

    success_count = len(filepaths)
    failed_count = len(failed_files)
    all_failed = True if success_count < 1 and failed_count > 0 else False
    dcc_store_data = {"status": True, "filepath": filepaths, "all-failed": all_failed}

    return status_display, dcc_store_data


@app.callback(
    [
        Output(component_id="parse-status", component_property="children"),
        Output(component_id="is-parse-begin", component_property="data")
    ],
    Input(component_id="is-upload-completed", component_property="data"),
    prevent_initial_call=True
)
def begin_parse(data: dict[str, bool | list[str] | None]) -> tuple[html.Div | dbc.Alert, dict[str, bool]]:
    status = data.get("status", False)
    is_all_failed = data.get("all-failed", False)

    if not status or is_all_failed:
        return html.Div(), {"status": False}

    message = [html.P("Preparing for parsing data. It may take some time.")]
    status_display = format_status_prompt(title="Parsing Data", msg=message, color="info", dismissable=False)
    is_parse_begin = {"status": True}

    return status_display, is_parse_begin


if __name__ == "__main__":
    pass

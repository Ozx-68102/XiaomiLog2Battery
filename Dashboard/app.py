import os

import dash
import dash_bootstrap_components as dbc
import dash_uploader as du
from dash import dcc, html, Output, Input, no_update, NoUpdate

from Modules.Core import init_graph
from Modules.FileProcess import INSTANCE_PATH
from .utils import format_status_prompt, upload_status_prompt

basepath = os.path.dirname(os.path.abspath(__file__))

app = dash.Dash(__name__, assets_folder=os.path.join(basepath, "assets"))
app.config.suppress_callback_exceptions = True

du.configure_upload(app=app, folder=INSTANCE_PATH)

__FAILED_FILES_LIST = []

app.layout = dbc.Container([
    # Those 3 stores will be modified by `upload-prompt.js` => js code
    dcc.Store(
        id="js-update-prompt",
        data={
            "show": False, "title": None, "msg": None, "color": "info", "dismissable": None
        }
    ),
    dcc.Store(id="js-new-error-file", data={"filename": None}),  # Get a new error file
    dcc.Store(id="js-error-file-empty-trigger", data={"status": None}),  # clear the FAILED_FILES_LIST
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
    global __FAILED_FILES_LIST
    __FAILED_FILES_LIST = []

    return no_update


@app.callback(
    Output(component_id="js-new-error-file", component_property="data"),
    Input(component_id="js-new-error-file", component_property="data"),
)
def add_new_error_file(data: dict[str, str]) -> NoUpdate:
    """
    Use a callback to add the error file to a global variable **__FAILED_FILES_LIST**.
    """
    global __FAILED_FILES_LIST
    unique_list = set(__FAILED_FILES_LIST)

    filename = data.get("filename", None)
    if filename and isinstance(filename, str):
        unique_list.add(filename)

    __FAILED_FILES_LIST = list(unique_list)

    return no_update


@app.callback(
    Output(component_id="upload-status", component_property="children", allow_duplicate=True),
    Input(component_id="js-update-prompt", component_property="data"),
    prevent_initial_call=True
)
def render_upload_0t1_prompt(data: dict[str, str | bool]) -> dbc.Alert | html.Div:
    """
    Render a prompt when upload beginning, operate by customized js file automatically.
    """
    keywords = ["title", "msg", "color"]
    if data.get("show") and any((data.get(keyword) is not None) for keyword in keywords):
        return format_status_prompt(title=data.get("title"), msg=[data.get("msg")], color=data.get("color"))

    return html.Div()


@du.callback(
    output=[
        Output(component_id="upload-status", component_property="children"),
        Output(component_id="output-container", component_property="children")
    ],
    id="upload-component"
)
def handle_upload(status: du.UploadStatus) -> tuple[dbc.Alert | html.Div, dbc.Alert | html.Div]:
    if not status.is_completed:
        failed_files = __FAILED_FILES_LIST
        status_message, color = upload_status_prompt(success=status.uploaded_files, failed=failed_files)
        status_display = format_status_prompt(title="Uploading...", msg=status_message, color=color, dismissable=False)
        return status_display, html.Div()

    filepath = [os.fspath(fp) for fp in status.uploaded_files]

    charts, num = init_graph(filepath_list=filepath)
    if not charts:
        status_display = format_status_prompt(
            title="Oops! An unexpected error occurred", msg=["Failed to generate Graphs."],
            color="danger", dismissable=False
        )
        return status_display, html.Div()

    msg_prefix = "The graph was" if num == 1 else "The graphs were"

    status_display = format_status_prompt(
        title="Successful!", msg=[f"{msg_prefix} generated successfully below."],
        color="success", dismissable=True
    )
    return status_display, charts


if __name__ == "__main__":
    pass

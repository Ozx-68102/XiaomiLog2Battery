import os
from pathlib import Path

import dash
import dash_bootstrap_components as dbc
import dash_uploader as du
from dash import dcc, html, Output, Input, no_update, NoUpdate

from Modules.Core import init_graph
from Modules.FileProcess import INSTANCE_PATH

basepath = os.path.dirname(os.path.abspath(__file__))

app = dash.Dash(__name__, assets_folder=os.path.join(basepath, "assets"))
app.config.suppress_callback_exceptions = True

du.configure_upload(app=app, folder=INSTANCE_PATH)

__FAILED_FILES_LIST = []

app.layout = dbc.Container([
    # Those stores will be modified by `upload-init-prompt.js` => js code
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
    dbc.Row(html.Div(id="status-container")),
    dbc.Row(html.Div(id="output-container", style={"display": "flex", "flexDirection": "column", "gap": "10px"}))
], fluid=True, style={"padding": "15px"})

def __show_alert(title: str, msg: list, color: str = "info", dismissable: bool | None = None) -> dbc.Alert:
    return dbc.Alert([
        html.H3(title),
        html.Hr(),
        html.Div(msg)
    ], color=color, dismissable=dismissable)


def __upload_status_handler(success: list[Path], failed: list[str]) -> tuple[list[html.P | html.Ul], str]:
    success_count = len(success)
    failed_count = len(failed)

    if success_count < 1 and failed_count < 1:
        return [html.P("Now files are uploading, it may take some time, so hang tight.")], "info"

    status = [html.P("Files still uploading...")]
    if failed_count > 0:
        failed_file_text = "was 1 file" if failed_count == 1 else f"were {failed_count} files"
        status.extend([
            html.H5("Please note:"),
            html.P(f"There {failed_file_text} that failed to upload:"),
            html.Ul([html.Li(f) for f in failed]),
            html.Br(), html.Br()
        ])

    filenames = [os.path.basename(os.fspath(filepath)) for filepath in success]
    if success_count > 0:
        success_file_text = "1 file was" if success_count == 1 else f"{success_count} files were"
        status.extend([
            html.P(f"System detected that {success_file_text} uploaded successfully:"),
            html.Ul([html.Li(f) for f in filenames])
        ])

    color = "warning" if failed_count > 0 else "info"
    return status, color


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
    Output(component_id="status-container", component_property="children", allow_duplicate=True),
    Input(component_id="js-update-prompt", component_property="data"),
    prevent_initial_call=True
)
def render_upload_0t1_prompt(data: dict[str, str | bool]) -> dbc.Alert | html.Div:
    """
    Render a prompt when upload beginning, operate by customized js file automatically.
    """
    keywords = ["title", "msg", "color"]
    if data.get("show") and any((data.get(keyword) is not None) for keyword in keywords):
        return __show_alert(title=data.get("title"), msg=[data.get("msg")], color=data.get("color"))

    return html.Div()


@du.callback(
    output=[
        Output(component_id="status-container", component_property="children"),
        Output(component_id="output-container", component_property="children")
    ],
    id="upload-component"
)
def handle_upload(status: du.UploadStatus) -> tuple[dbc.Alert | html.Div, dbc.Alert | html.Div]:
    if not status.is_completed:
        failed_files = __FAILED_FILES_LIST
        status_message, color = __upload_status_handler(success=status.uploaded_files, failed=failed_files)
        status_display = __show_alert(title="Uploading...", msg=status_message, color=color, dismissable=False)
        return status_display, html.Div()

    filepath = [os.fspath(fp) for fp in status.uploaded_files]
    charts, num = init_graph(filepath_list=filepath)
    if not charts:
        status_display = __show_alert(
            title="Oops! An unexpected error occurred", msg=["Failed to generate Graphs."],
            color="danger", dismissable=False
        )
        return status_display, html.Div()

    msg_prefix = "The graph was" if num == 1 else "The graphs were"

    status_display = __show_alert(
        title="Successful!", msg=[f"{msg_prefix} generated successfully below."],
        color="success", dismissable=True
    )
    return status_display, charts


if __name__ == "__main__":
    pass

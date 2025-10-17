import os

import dash
import dash_bootstrap_components as dbc
import dash_uploader as du
from dash import html, Output

from Modules.Core import init_graph
from Modules.FileProcess import INSTANCE_PATH

basepath = os.path.dirname(os.path.abspath(__file__))

app = dash.Dash(__name__, assets_folder=os.path.join(basepath, "assets"))
app.config.suppress_callback_exceptions = True

du.configure_upload(app=app, folder=INSTANCE_PATH)

app.layout = dbc.Container([
    dbc.Row(
        dbc.Col(html.H1("Battery Log Analyzer", className="text-center my-4"), width=12)
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
                        text="Drag files to here, or click it to select file(s). After that file(s) will be automatically uploaded.",
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


@du.callback(
    output=[
        Output("status-container", "children"),
        Output("output-container", "children"),
    ],
    id="upload-component"
)
def handle_upload(status: du.UploadStatus) -> tuple[dbc.Alert | html.Div, dbc.Alert | html.Div]:
    # TODO: This function will be called while a file was uploaded.
    #  Not begin uploading, so the prompt won't appear immediately.
    #  If upload failed, it will not be called.
    if not status.is_completed:
        file_count = len(status.uploaded_files)
        if file_count < 1:
            status_message = [html.P("Now files are uploading, it may take some time, so hang tight.")]
        elif file_count == 1:
            filename = [os.path.basename(os.fspath(fp)) for fp in status.uploaded_files][0]
            status_message = [
                html.P("Files still uploading..."),
                html.P("System detected that 1 file was uploaded successfully:"),
                html.Ul([html.Li(filename)])
            ]
        else:
            filenames = [os.path.basename(os.fspath(fp)) for fp in status.uploaded_files]
            status_message = [
                html.P("Files still uploading..."),
                html.P(f"System detected that {file_count} files were uploaded successfully:"),
                html.Ul([html.Li(fn) for fn in filenames])
            ]

        status_display = dbc.Alert([
            html.H3("Uploading..."),
            html.Hr(),
            html.Div(status_message)
        ], color="info", dismissable=False)
        return status_display, html.Div()


    filepath = [os.fspath(fp) for fp in status.uploaded_files]
    charts = init_graph(filepath_list=filepath)
    if not charts:
        status_display = dbc.Alert([
            html.H3("Oops! An unexpected error occurred"),
            html.Hr(),
            html.Div("Failed to generate Graphs.")
        ], color="danger", dismissable=False)
        return status_display, html.Div()

    status_display = dbc.Alert([
        html.H3("Successful!"),
        html.Hr(),
        html.Div("The graphs were generated successfully below.")
    ])
    return status_display, charts


if __name__ == "__main__":
    pass

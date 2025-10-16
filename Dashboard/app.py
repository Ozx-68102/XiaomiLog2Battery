import os

import dash
import dash_bootstrap_components as dbc
import dash_uploader as du
from dash import html, Output

from Modules.Core import init_graph
from Modules.FileProcess import INSTANCE_PATH

basepath = os.path.dirname(os.path.abspath(__file__))
save_path = os.path.join(INSTANCE_PATH, "upload")
os.makedirs(save_path, exist_ok=True)

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
    html.Div(id="output-container", style={"display": "flex", "flexDirection": "column", "gap": "10px"}),
], fluid=True, style={"padding": "15px"})


@du.callback(output=Output("output-container", "children"), id="upload-component")
def handle_upload(status: du.UploadStatus) -> html.Div:
    return init_graph(status=status)


if __name__ == "__main__":
    pass

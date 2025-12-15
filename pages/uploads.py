import dash
import dash_bootstrap_components as dbc
import dash_uploader_uppy5 as du
from dash import html, Output, Input

from utils import format_alert_content

MAX_FILE_SIZE = 20 * 1024
MAX_FILE_NUMBER = 100

dash.register_page(__name__, path="/uploads")

layout = [
    dbc.Row(
        dbc.Col(
            [
                html.H2("Upload your Xiaomi log files"),
                html.Br(),
                du.Upload(
                    id="uploader",
                    note=f"You can upload no more than {MAX_FILE_SIZE} MB, or {MAX_FILE_NUMBER} files at a time.",
                    allowed_file_types=[".zip"],
                    max_total_file_size=20 * 1024,
                    max_number_of_files=100,
                    upload_id="uploads",
                )
            ],
            xs=12, md=10, lg=8, xl=6,
        ),
        justify="center",
    ),
    html.Br(),
    dbc.Alert(
        id="alert",
        children=[],
        color=None,
        is_open=False,
        dismissable=True,
        fade=True
    )
]

@dash.callback(
    [
        Output("alert", "is_open"),
        Output("alert", "children"),
        Output("alert", "color")
    ],
    [
        Input("uploader", "uploadedFiles"),
        Input("uploader", "failedFiles")
    ],
    prevent_initial_call=True
)
def anonymous(uploaded_files: list[dict[str, str | int | dict[str, str | int]]], failed_files: list[dict[str, str]]):
    output = f"uploaded: {uploaded_files} failed: {failed_files}"
    return True, format_alert_content(title="Completed", content=output), "info"
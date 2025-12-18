import dash
import dash_bootstrap_components as dbc
import dash_uploader_uppy5 as du
from dash import html, dcc, Output, Input, no_update

from utils import format_alert_content

MAX_FILE_SIZE = 20 * 1024
MAX_FILE_NUMBER = 100

dash.register_page(__name__, path="/uploads", order=2, name="Uploads")

layout = [
    dbc.Row(
        dbc.Col(
            [
                html.Strong("Upload Xiaomi log files"),
                html.Br(),
                du.Upload(
                    id="uploader",
                    note=f"You can upload no more than {MAX_FILE_SIZE} MB, or {MAX_FILE_NUMBER} files at a time.",
                    allowed_file_types=[".zip"],
                    max_total_file_size=20 * 1024,
                    max_number_of_files=100,
                )
            ],
            xs=12, md=10, lg=8, xl=6,
        ),
        justify="center",
    ),
    html.Br(),
    dbc.Row(
        dbc.Col(
            dbc.Alert(
                id="upload-alert",
                children=[],
                color=None,
                is_open=False,
                dismissable=True,
                fade=True
            ),
            xs=12, md=10, lg=8, xl=6,
        ),
        justify="center",
    )
]

@dash.callback(
    [
        Output("upload-alert", "is_open"),
        Output("upload-alert", "children"),
        Output("upload-alert", "color")
    ],
    [
        Input("uploader", "uploadedFiles"),
        Input("uploader", "failedFiles")
    ],
    prevent_initial_call=True
)
def upload_handler(
        uploaded_files: list[dict[str, str | int | dict[str, str | int]]],
        failed_files: list[dict[str, str]]
) -> tuple[bool, list[dbc.Row], str]:
    count_success = len(uploaded_files)
    count_failed = len(failed_files)

    if count_success == 0 and count_failed == 0:
        return (no_update, ) * 3

    if count_success > 0:
        output = [
            "Upload successful. You can click ",
            dcc.Link("here", href="/processing", className="alert-link"),
            " for the next step."
        ]

        if count_failed == 0:
            return True, format_alert_content(title="INFO", content=output), "info"

        output.extend([
            html.Br(),
            "But some errors occurred while uploading: ",
            html.Ul([html.Li(f"Filename: {failed["name"]}, Error: {failed["error"]}") for failed in failed_files])
        ])
        return True, format_alert_content(title="INFO", content=output), "warning"

    if count_failed > 0:
        output = [
            "Upload failed. Here are the errors, maybe you can try again later:",
            html.Ul([html.Li(f"Filename: {failed["name"]}, Error: {failed["error"]}") for failed in failed_files])
        ]
        return True, format_alert_content(title="NOTE", content=output), "danger"

    return (no_update, ) * 3

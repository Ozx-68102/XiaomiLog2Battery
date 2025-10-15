import os
from datetime import datetime

import dash
import dash_bootstrap_components as dbc
import dash_uploader as du
from dash import html, Output

from Modules.FileProcess import INSTANCE_PATH

basepath = os.path.dirname(os.path.abspath(__file__))
save_path = os.path.join(INSTANCE_PATH, "upload")
os.makedirs(save_path, exist_ok=True)

app = dash.Dash(__name__, assets_folder=os.path.join(basepath, "assets"))
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
    html.Div(id="output-message"),
    html.Div(id="file-metadata-display-zone")
], fluid=True, style={"padding": "15px"})


def format_filesize(size: int) -> str:
    if size == 0:
        return "0 B"

    size_types = ["B", "KB", "MB", "GB"]
    i = 0
    while size > 1024 and i < len(size_types) - 1:
        size /= 1024.0
        i += 1

    return f"{size:.2f} {size_types[i]}"


def get_file_metadata(fp: str) -> dict[str, str]:
    try:
        stat_info = os.stat(fp)
        filesize = format_filesize(stat_info.st_size)
        upload_time = datetime.fromtimestamp(stat_info.st_mtime).strftime("%Y-%m-%d %H:%M:%S")

        return {
            "filesize": filesize,
            "upload_time": upload_time,
            "filepath": fp
        }
    except Exception as e:
        print(e)
        return {
            "filesize": "Unknown",
            "upload_time": "Unknown",
            "filepath": fp
        }


@du.callback(output=[
    Output("output-message", "children"),
    Output("file-metadata-display-zone", "children")
], id="upload-component")
def handle_upload(status: du.UploadStatus):
    print(f"Upload completed. Upload status: {status.n_uploaded}/{status.n_total}")
    print(f"Is completed: {status.is_completed}")

    if not status.is_completed:
        return html.Div(), html.Div()

    success = {}
    for filepath in status.uploaded_files:
        filename = os.path.basename(filepath)
        metadata = get_file_metadata(filepath)
        success[filename] = metadata
        print(f"Successfully uploaded: {filename}")

    success_count = len(success)
    if success_count > 0:
        success_msg = dbc.Alert([
            html.H4("Successfully uploaded!", className="alert-heading"),
            html.P(f"{success_count} file(s) has/have already been uploaded:"),
            html.Ul([html.Li(fn) for fn in success.keys()]),
        ], color="success", dismissable=True)
        failed_color = "warning"
    else:
        success_msg = html.Div()
        failed_color = "danger"

    failed_count = status.n_total - status.n_uploaded
    failed_msg = dbc.Alert([
        html.H4("Some files may have failed to upload", className="alert-heading"),
        html.P(f"Expected {status.n_total} files, but only {status.n_uploaded} were uploaded successfully."),
    ], color=failed_color, dismissable=True) if failed_count > 0 else html.Div()

    output_msg = html.Div([success_msg, failed_msg])
    if success_count < 1:
        return output_msg, html.Div()

    metadata_cards = []
    for fn, meta in success.items():
        card = dbc.Card([
            dbc.CardHeader(f"Filename: {fn}"),
            dbc.CardBody([
                dbc.ListGroup([
                    dbc.ListGroupItem(f"File size: {meta["filesize"]}"),
                    dbc.ListGroupItem(f"Update Time: {meta["upload_time"]}")
                ], flush=True)
            ])
        ], className="mb-3")
        metadata_cards.append(card)

    metadata_display = html.Div([
        html.Hr(),
        html.H4("File Information"),
        *metadata_cards
    ])

    return output_msg, metadata_display


if __name__ == "__main__":
    pass

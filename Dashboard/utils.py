import os
from pathlib import Path

import dash_bootstrap_components as dbc
from dash import html


def format_status_prompt(title: str, msg: list, color: str = "info", dismissable: bool | None = None) -> dbc.Alert:
    return dbc.Alert([
        html.H3(title),
        html.Hr(),
        html.Div(msg)
    ], color=color, dismissable=dismissable)


def upload_status_prompt(success: list[Path], failed: list[str], complete: bool) -> tuple[list[html.P | html.Ul], str]:
    success_count = len(success)
    failed_count = len(failed)

    if success_count < 1 and failed_count < 1:
        if not complete:
            return [html.P("Now files are uploading, it may take some time, so hang tight.")], "info"

        # maybe it will not reach here but just in case
        return [html.P("An unexpected error occurred.")], "danger"

    status = [html.P("Files still uploading...")] if not complete else []
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

    if complete:
        if success_count > 0:
            return status, "success" if failed_count < 1 else "warning"

        return status, "danger"

    return status, "info" if failed_count < 1 else "warning"

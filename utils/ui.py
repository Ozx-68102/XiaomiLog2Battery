import dash_bootstrap_components as dbc
from dash import html


def format_alert_content(title: str, content: str) -> list[dbc.Row]:
    return [
        dbc.Row(html.H4(title)),
        dbc.Row(html.Hr()),
        dbc.Row(html.Div(content))
    ]

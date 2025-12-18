import dash
import dash_bootstrap_components as dbc
from dash import html, dcc

from src import APP_VERSION

dash.register_page(__name__, path="/", order=1, name="Home")


def get_card(title: str, desc: str, icon: str, href: str, btn_text: str, color: str = "primary"):
    return dbc.Card(
        [
            dbc.CardBody(
                [
                    html.Div(
                        html.I(className=f"bi {icon} display-4 text-{color}"),
                        className="mb-3"
                    ),
                    html.H4(title, className="card-title fw-bold"),
                    html.P(desc, className="card-text text-muted flex-grow-1"), # flex-grow-1 保证文字高度对齐
                    dcc.Link(
                        dbc.Button(btn_text, color=color, outline=True, className="w-100 mt-3"),
                        href=href,
                        style={"textDecoration": "none"}
                    )
                ],
                className="d-flex flex-column text-center h-100"
            )
        ],
        className="h-100 shadow-sm border-0 hover-shadow transition-all"
    )

layout = dbc.Container([
    html.Div([
        html.H1([
            html.I(className="bi bi-battery-charging me-3 text-primary"),
            "XiaomiLog2Battery"
        ], className="display-4 fw-bold mb-3"),

        html.P(
            "A practical tool to extract, analyze, and visualize battery health data from Xiaomi system logs.",
            className="lead text-secondary mb-4"
        ),
        html.Hr(className="my-5 w-50 mx-auto"),
    ], className="text-center py-5"),

    dbc.Row([
        html.H3("Workflow", className="text-center mb-4 fw-light"),

        # Step 1: Upload
        dbc.Col([
            get_card(
                title="1. Upload Logs",
                desc="Upload your Xiaomi debug logs (bugreport-*.zip or raw text files). Supports batch uploading.",
                icon="bi-cloud-arrow-up",
                href="/uploads",
                btn_text="Go to Upload",
                color="primary"
            )
        ], width=12, md=6, lg=3, className="mb-4"),

        # Step 2: Process
        dbc.Col([
            get_card(
                title="2. Process Data",
                desc="Parse raw logs, extract battery capacity fields, and clean the data for analysis.",
                icon="bi-cpu",
                href="/processing",
                btn_text="Start Processing",
                color="success"
            )
        ], width=12, md=6, lg=3, className="mb-4"),

        # Step 3: Graphs
        dbc.Col([
            get_card(
                title="3. Visualize",
                desc="View interactive charts showing capacity trends, battery health, and degradation over time.",
                icon="bi-graph-up-arrow",
                href="/graphs",
                btn_text="View Charts",
                color="info"
            )
        ], width=12, md=6, lg=3, className="mb-4"),

        # Step 4: Report
        dbc.Col([
            get_card(
                title="4. Detailed Report",
                desc="Inspect row-level data including learned capacity, voltages, and cycle counts in a grid view.",
                icon="bi-table",
                href="/reports",
                btn_text="View Data",
                color="warning"
            )
        ], width=12, md=6, lg=3, className="mb-4"),
    ], className="mb-5"),

    dbc.Row([
        dbc.Col([
            dbc.Alert(
                [
                    html.H5("System Preferences", className="alert-heading"),
                    html.P("Need to adjust the timezone or manage global settings?", className="mb-0"),
                    html.Hr(),
                    dcc.Link("Go to Settings", href="/settings", className="alert-link")
                ],
                color="light",
                className="shadow-sm border"
            )
        ], width=12, md=8, lg=6, className="mx-auto")
    ], className="text-center mb-5"),

    html.Div([
        html.Small(f"Designed for Xiaomi Devices • Version {APP_VERSION}", className="text-muted")
    ], className="text-center pb-4")

], fluid=True)
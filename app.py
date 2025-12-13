import dash
import dash_bootstrap_components as dbc
from dash import Dash, html

app = Dash(__name__, use_pages=True, assets_folder="./assets")

app.layout = html.Div([
    dbc.NavbarSimple([
        dbc.NavItem(dbc.NavLink(page["name"], href=page["relative_path"]))
        for page in dash.page_registry.values()
    ],
        brand=html.Strong("XiaomiLog2Battery"),
        brand_href="/",
        color="primary",
        dark=True
    ),
    dbc.Container(
        dash.page_container,
        fluid=True,
        class_name="mt-4"
    )
])
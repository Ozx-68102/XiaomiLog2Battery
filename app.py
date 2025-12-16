import dash
import dash_bootstrap_components as dbc
import dash_uploader_uppy5 as du
from dash import Dash, html

from src import UPLOAD_PATH

app = Dash(__name__, use_pages=True, assets_folder="./assets")
du.configurator(app, folder=str(UPLOAD_PATH), use_upload_id=False)

app.layout = html.Div([
    dbc.NavbarSimple([
        dbc.NavItem(dbc.NavLink(page["name"], href=page["relative_path"]))
        for page in dash.page_registry.values()
    ],
        brand=html.Strong("XiaomiLog2Battery"),
        brand_href="javascript: void(0);",
        color="primary",
        dark=True
    ),
    dbc.Container(
        dash.page_container,
        fluid=True,
        class_name="mt-4"
    )
])
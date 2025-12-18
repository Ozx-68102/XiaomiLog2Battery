import dash
import dash_bootstrap_components as dbc
import dash_uploader_uppy5 as du
import diskcache
from dash import Dash, dcc, html, DiskcacheManager, Output, Input, State

from src import UPLOAD_PATH, DISKCACHE_PATH

cache = diskcache.Cache(str(DISKCACHE_PATH))
app = Dash(
    __name__,
    use_pages=True,
    assets_folder="./assets",
    background_callback_manager=DiskcacheManager(cache)
)

du.configurator(app, folder=str(UPLOAD_PATH), use_upload_id=False)

app.layout = html.Div([
    dcc.Store(id="global-timezone", storage_type="local", data="UTC"),
    dbc.Navbar(
        dbc.Container([
            html.Div([
                dbc.NavbarBrand(
                    "XiaomiLog2Battery",
                    href="javascript: void(0);",
                    class_name="me-0 fw-bold",
                ),
                dcc.Link(
                    dbc.Badge(
                        id="navbar-timezone-displayer",
                        color="light",
                        text_color="dark",
                        class_name="border border-secondary small py-1",
                    ),
                    href="/settings",
                    className="ms-3 align-self-center",
                    style={"textDecoration": "none"},
                    title="Click to change timezone setting",
                ),
            ], className="d-flex"),
            dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
            dbc.Collapse(
                dbc.Nav([
                    dbc.NavItem(dbc.NavLink(page["name"], href=page["relative_path"], external_link=False))
                    for page in dash.page_registry.values()
                ], class_name="ms-auto", navbar=True),
                id="navbar-collapse",
                navbar=True,
            ),
        ], fluid=True),
        color="primary",
        dark=True,
        class_name="shadow-sm",
        expand="lg"
    ),
    dbc.Container(
        dash.page_container,
        fluid=True,
        class_name="mt-4"
    )
])


@app.callback(
    Output("navbar-timezone-displayer", "children"),
    Input("global-timezone", "data"),
)
def update_navbar_tz(timezone: str) -> list[html.I | str]:
    return [
        html.I(className="bi bi-globe me-2"),
        f"Timezone: {timezone}",
    ]


@app.callback(
    Output("navbar-collapse", "is_open"),
    Input("navbar-toggler", "n_clicks"),
    State("navbar-collapse", "is_open"),
)
def toggle_navbar_collapse(n_click: int, is_open: bool) -> bool:
    return not is_open if n_click else is_open

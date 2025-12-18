import dash

from dash import html

dash.register_page(__name__, path="/", order=1, name="Home")

layout = html.H2("Welcome to use XiaomiLog2Battery Dashboard!")
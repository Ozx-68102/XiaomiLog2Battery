import dash

from dash import html

dash.register_page(__name__, path="/processing", order=3)

layout = html.Div("Welcome to processing website! Now it's developing...")


import webbrowser
from threading import Timer

import dash
from dash import html

app = dash.Dash(__name__)
app.layout = html.Div([
    html.H1("Battery Log Analyzer", style={"textAlign": "center"})
], style={"padding": "20px"})

#
def open_browser() -> None:
    webbrowser.open_new_tab("http://localhost:8050/")


if __name__ == "__main__":
    Timer(0.5, open_browser).start()
    app.run()
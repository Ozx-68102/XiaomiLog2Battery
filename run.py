import webbrowser
from threading import Timer

from Dashboard.app import app


def open_browser() -> None:
    webbrowser.open_new_tab("http://localhost:8050/")


if __name__ == "__main__":
    Timer(0.5, open_browser).start()
    app.run()
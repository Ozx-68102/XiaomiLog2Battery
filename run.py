import webbrowser
from threading import Timer

from waitress import serve

from Dashboard import app


def open_browser() -> None:
    webbrowser.open_new_tab("http://localhost:8050/")


if __name__ == "__main__":
    try:
        print("Starting Server...")
        Timer(0.5, open_browser).start()
        serve(app.server, host="127.0.0.1", port=8050)
    except Exception as e:
        print("Server failed to start.")
        raise e

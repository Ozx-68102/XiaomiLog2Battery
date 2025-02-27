from WebPanel import create_app
import webbrowser
from threading import Timer

app = create_app()
quick_start = False

def open_browser():
    global quick_start
    if not quick_start:
        webbrowser.open_new_tab(f"http://localhost:5000/")
        quick_start = True


if __name__ == "__main__":
    Timer(0.5, open_browser).start()
    app.run(host="localhost", port=5000, debug=False)   # if 'debug' is True, 'Timer' will execute it twice

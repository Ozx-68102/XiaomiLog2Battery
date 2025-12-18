# XiaomiLog2Battery

![Python](https://img.shields.io/badge/Python-3.13-blue.svg)
![Dash](https://img.shields.io/badge/Framework-Dash_3.3.0+-00796B.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

**XiaomiLog2Battery** is a practical tool designed to extract, analyze, and visualize battery health data from Xiaomi smartphone system logs (`bugreport`).



## Important Disclaimer

The battery capacity analysis results provided by this tool are calculated based on system logs and **may differ from official Xiaomi after-sales testing results**.

Please always rely on official diagnostic results from Xiaomi Service Centers for warranty claims or battery replacement decisions.



## Key Features

- **Automated Log Processing**: Drag-and-drop Xiaomi `bugreport-*.zip` files.
- **Interactive Visualizations**:
    - **Trend Charts**: Track `Learned Capacity`, `Hardware Capacity`, and `Design Capacity` over time.
    - **Health Dashboard**: Visual representation of battery wear and tear.
- **Detailed Data Report**:
    - Powered by **Dash AG Grid** for advanced sorting, filtering, and row-level inspection.
    - View critical metrics like `Min/Max Learned Capacity` and voltage snapshots.
- **Global Time Zone Support**: Automatically converts UTC timestamps from logs to your local time zone (configurable via Settings).
- **Persistent Storage**: Uses **SQLite** for efficient, local data storage. Supports appending new logs to existing history.

- **High Performance**:
    - **Waitress WSGI Server**: Multi-threaded production-ready server for a responsive UI.
    - **`Diskcache`**: Manages background callbacks to handle large file processing without freezing the interface.
    - **Robust File Upload**: Powered by **[dash-uploader-uppy5](https://github.com/Ozx-68102/dash-uploader-uppy5)**, a high-performance upload component developed by myself.



## Technology Stack

This project is built with a modern Python stack.

| Component        | Technology              | Description                                                                               |
|------------------|-------------------------|-------------------------------------------------------------------------------------------|
| **Frontend**     | **Dash 3.3.0**          | Built using the **Dash Pages** structure for multi-page routing.                          |
| **UI Framework** | **Bootstrap 5**         | Responsive layout via `dash-bootstrap-components`.                                        |
| **Data Grid**    | **Dash AG Grid**        | Enterprise-grade data tables for the Report page.                                         |
| **File Upload**  | **dash-uploader-uppy5** | Custom component developed by [myself](https://github.com/Ozx-68102/dash-uploader-uppy5). |
| **Backend**      | **Waitress**            | Production-quality WSGI server (Multi-threaded).                                          |
| **Async Tasks**  | **Diskcache**           | Handles background parsing tasks.                                                         |
| **Data & Logic** | **Pandas & SQLite**     | High-performance data manipulation and persistence.                                       |
| **Dependency**   | **uv**                  | Modern dependency management using `pyproject.toml`.                                      |



## Requirements

- **Python**: **3.13.x** (Strictly required)



## Installation & Setup

This project provides a **`uv.lock`** file for deterministic builds. Using **uv** is the fastest and most reliable way to run this application.

1. **Install `uv`**: [click here for more installation details](https://docs.astral.sh/uv/#installation)

2. **Sync & Run**

    ```bash
    uv sync
    uv run run.py
    ```



## Usage Workflow

1. **Launch**: Run `python run.py` (or `uv run run.py`). The browser will automatically open at `http://localhost:8050/`.
2. **Upload**: Go to the **Uploads** page and drop your `bugreport-*.zip` files.
3. **Process**: Navigate to the **Processing** page to parse the uploaded files into the local database.
4. **Visualize**:
    - **Graphs**: View visual trends of your battery health.
    - **Report**: Inspect detailed numbers in the data grid.
5. **Settings**: Go to **Settings** to configure your local time zone (e.g., `Asia/Shanghai`) if the timestamps look incorrect.



## Project Structure

```text
XiaomiLog2Battery/
├── app.py                  # Main application instance (Navbar, Server config)
├── run.py                  # Entry point (Dependency check + Waitress server)
├── pyproject.toml          # Project configuration & Dependencies
├── uv.lock                 # Lockfile for reproducible builds
│
├── pages/                  # Frontend Views (Dash Pages)
│   ├── home.py             # Landing page
│   ├── uploads.py          # File upload interface
│   ├── processing.py       # Data parsing logic
│   ├── graphs.py           # Visual analytics
│   ├── report.py           # AG Grid detailed report
│   └── settings.py         # Timezone & System preferences
│
├── src/                    # Backend Logic
│   ├── analysis/           # Visualizer & Parser services
│   ├── processing/         # File extraction & Management
│   ├── persistence/        # SQLite database operations
│   └── config.py           # Global constants & Version reading
│
├── utils/                  # Helper scripts
├── assets/                 # Static files (CSS, Images)
└── instance/               # Runtime data (Database, Cache, Uploads)
```



## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

**Areas for improvement:**

- Support for parsing logs from other Android manufacturers.
- More advanced battery health prediction algorithms.



## License

MIT License © 2025 Ozx-68102

import os
from typing import Literal

import dash_bootstrap_components as dbc
from dash import html, dcc

from Modules.DataAnalysis import BatteryInfoParser, BatteryDataService, PlotlyVisualizer
from Modules.FileProcess import BatteryLogProcessor, FolderOperator, TXT_PATH

_log_processor = BatteryLogProcessor()
_info_parser = BatteryInfoParser()
_data_service = BatteryDataService()
_visualizer = PlotlyVisualizer()
_folder_operator = FolderOperator()


def _calculate_workers(mode: Literal["low", "balanced", "high"], file_count: int) -> int:
    """
    Calculate the number of workers based on mode, file count, and CPU count.
    :param mode: The performance mode (low, balanced, high).
    :param file_count: Number of files to process.
    :raise ValueError: If mode is invalid.
    :return: Calculated number of workers.
    """
    cpu_count = os.cpu_count() or 1
    if mode == "low":
        # Low mode: min(cpu_count // 2, file_count, 4)
        return min(max(cpu_count // 2, 1), file_count, 4)
    elif mode == "balanced":
        # Balanced mode: min(int(cpu_count * 0.75), file_count, 6)
        return min(max(int(cpu_count * 0.75), 1), file_count, 6)
    elif mode == "high":
        # High mode: min(cpu_count, file_count, 8) - original logic
        return min(cpu_count, file_count, 8)

    raise ValueError("Invalid mode.")


def parse_files(filepath_list: list[str], thread_count_mode: Literal["low", "balanced", "high"] = "balanced") -> list[
    dict[str, str | int]]:
    print(f"Start to process {len(filepath_list)} zip file(s).")

    # Clear all previously extracted files before processing new uploads
    try:
        _folder_operator.reset_dir(path=TXT_PATH)
        print("Cleared all previously extracted files.")
    except Exception as e:
        print(f"Warning: Failed to clear extracted files: {e}")

    thread_count = _calculate_workers(mode=thread_count_mode, file_count=len(filepath_list))
    print(f"Using {thread_count} worker(s) for processing (mode: {thread_count_mode}).")

    txt_list = _log_processor.process_xiaomi_log(fps=filepath_list, thread_count=thread_count)
    print(f"Done with {len(txt_list)} txt file(s).")

    print(f"Start to parse {len(txt_list)} txt file(s).")
    # Use the same thread count for parsing
    thread_count_parse = _calculate_workers(mode=thread_count_mode, file_count=len(txt_list))
    battery_info = _info_parser.parse_battery_info(tps=txt_list, thread_count=thread_count_parse)
    print(f"Done with {len(battery_info)} battery info.")
    return battery_info


def store_data(data: list[dict[str, str | int]], mode: str = "init") -> bool:
    print(f"Start to store {len(data)} data into database with mode: {mode}.")
    
    if mode == "add":
        # Append data to existing table
        print("Appending new data to existing records...")
        status = _data_service.append_battery_data(data=data)
    else:
        # Initialize table and store data
        print("Initializing table and storing data...")
        status = _data_service.init_battery_data(data=data)
    
    print(f"Result: {status}")
    return status


def get_max_cycle_count() -> str:
    """
    Get the maximum cycle count from database.
    :return: Maximum cycle count as string, or "N/A" if no data.
    """
    battery_data = _data_service.get_all_battery_data()
    if not battery_data:
        return "N/A"

    cycle_counts = [item.get("cycle_count") for item in battery_data if item.get("cycle_count") is not None]
    if cycle_counts:
        return str(max(cycle_counts))
    return "N/A"


def viz_battery_data() -> tuple[dbc.Container | None, int]:
    print("Start to visualize battery data.")
    battery_data = _data_service.get_all_battery_data()
    if not battery_data:
        print("No battery data found in database.")
        return None, 0


    changing_chart = dcc.Graph(figure=_visualizer.gen_battery_changing_chart(data=battery_data))
    graph_count = 1

    try:
        health_chart = dcc.Graph(figure=_visualizer.gen_battery_health_chart(data=battery_data))
        graph_count += 1
    except ValueError:
        print("Your phone modal is not supported for health chart.")
        health_chart = html.Div()

    print(f"Done with visualizing {graph_count} graph(s).")

    if graph_count == 1:
        # Only changing chart
        return dbc.Container([
            dbc.Row([
                dbc.Col(changing_chart, width=12),
                health_chart
            ])
        ], fluid=True), graph_count
    else:
        # Both charts with responsive layout
        return dbc.Container([
            dbc.Row([
                dbc.Col(changing_chart, md=12, lg=6, className="mb-4"),
                dbc.Col(health_chart, md=12, lg=6, className="mb-4")
            ])
        ], fluid=True), graph_count


if __name__ == "__main__":
    pass

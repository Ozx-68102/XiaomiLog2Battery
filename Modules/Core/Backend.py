from dash import html, dcc

from Modules.DataAnalysis import BatteryInfoParser, BatteryDataService, PlotlyVisualizer
from Modules.FileProcess import BatteryLogProcessor, FolderOperator, TXT_PATH

_log_processor = BatteryLogProcessor()
_info_parser = BatteryInfoParser()
_data_service = BatteryDataService()
_visualizer = PlotlyVisualizer()
_folder_operator = FolderOperator()


def parse_files(filepath_list: list[str]) -> list[dict[str, str | int]]:
    print(f"Start to process {len(filepath_list)} zip file(s).")

    # Clear all previously extracted files before processing new uploads
    try:
        _folder_operator.reset_dir(path=TXT_PATH)
        print("Cleared all previously extracted files.")
    except Exception as e:
        print(f"Warning: Failed to clear extracted files: {e}")

    txt_list = _log_processor.process_xiaomi_log(fps=filepath_list)
    print(f"Done with {len(txt_list)} txt file(s).")

    print(f"Start to parse {len(txt_list)} txt file(s).")
    battery_info = _info_parser.parse_battery_info(tps=txt_list)
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


def viz_battery_data() -> tuple[html.Div | None, int]:
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
        print("Your modal is not supported for health chart.")
        health_chart = html.Div()

    print(f"Done with visualizing {graph_count} graph(s).")
    return html.Div([changing_chart, health_chart], style={"display": "flex"}), graph_count

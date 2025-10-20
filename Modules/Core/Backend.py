from dash import html, dcc

from Modules.DataAnalysis import BatteryInfoParser, BatteryDataService, PlotlyVisualizer
from Modules.FileProcess import BatteryLogProcessor

_log_processor = BatteryLogProcessor()
_info_parser = BatteryInfoParser()
_data_service = BatteryDataService()
_visualizer = PlotlyVisualizer()


def parse_files(filepath_list: list[str]) -> list[dict[str, str | int]]:
    print(f"Start to process {len(filepath_list)} zip file(s).")
    txt_list = _log_processor.process_xiaomi_log(fps=filepath_list)
    print(f"Done with {len(txt_list)} txt file(s).")

    print(f"Start to parse {len(txt_list)} txt file(s).")
    battery_info = _info_parser.parse_battery_info(tps=txt_list)
    print(f"Done with {len(battery_info)} battery info.")
    return battery_info


def store_data(data: list[dict[str, str | int]]) -> bool:
    print(f"Start to store {len(data)} data into database.")
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

from dash import html, dcc

from Modules.DataAnalysis import BatteryInfoParser, BatteryDataService, PlotlyVisualizer
from Modules.FileProcess import BatteryLogProcessor

_log_processor = BatteryLogProcessor()
_info_parser = BatteryInfoParser()
_data_service = BatteryDataService()
_visualizer = PlotlyVisualizer()


def init_graph(filepath_list: list[str]) -> html.Div | None:
    print("Uploaded successfully.")

    print("Start to process zip file(s).")
    txt_list = _log_processor.process_xiaomi_log(fps=filepath_list)
    print(f"Done with {len(txt_list)} txt file(s).")

    print("Start to parse txt file(s).")
    battery_info = _info_parser.parse_battery_info(tps=txt_list)
    print(f"Done with {len(battery_info)} battery info.")

    # TODO: Here and database end need to set a `TRUNCATE` logic to adapt to `initial graph` function.
    #  Otherwise it will throw Database Error when use it multiple time
    print("Start to save battery info to database.")
    if not _data_service.save_battery_data(data=battery_info):
        print("Failed to save battery data.")
        return None

    print("Start to visualize needed graph.")
    vis_data = _data_service.get_all_battery_data()
    changing_chart = _visualizer.gen_battery_changing_chart(data=vis_data)
    health_chart = _visualizer.gen_battery_health_chart(data=vis_data)

    return html.Div([
        dcc.Graph(figure=changing_chart),
        dcc.Graph(figure=health_chart)
    ], style={"display": "flex"})

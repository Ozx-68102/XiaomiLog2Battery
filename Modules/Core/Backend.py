import os

import dash_uploader as du
from dash import html, dcc

from Modules.DataAnalysis import BatteryInfoParser, BatteryDataService, PlotlyVisualizer
from Modules.FileProcess import BatteryLogProcessor

_log_processor = BatteryLogProcessor()
_info_parser = BatteryInfoParser()
_data_service = BatteryDataService()
_visualizer = PlotlyVisualizer()


def init_graph(status: du.UploadStatus) -> html.Div:
    print(f"Is completed: {status.is_completed}")
    if not status.is_completed:
        return html.Div()

    print("Uploaded successfully.")
    uploaded_files = [os.fspath(fp) for fp in status.uploaded_files]

    print("Start to process zip file(s).")
    txt_list = _log_processor.process_xiaomi_log(fps=uploaded_files)
    print(f"Done with {len(txt_list)} txt file(s).")

    print("Start to parse txt file(s).")
    battery_info = _info_parser.parse_battery_info(tps=txt_list)
    print(f"Done with {len(battery_info)} battery info.")

    print("Start to save battery info to database.")
    if not _data_service.save_battery_data(data=battery_info):
        print("Failed to save battery data.")
        return html.Div()

    print("Start to visualize needed graph.")
    vis_data = _data_service.get_all_battery_data()
    changing_chart = _visualizer.gen_battery_changing_chart(data=vis_data)
    health_chart = _visualizer.gen_battery_health_chart(data=vis_data)

    return html.Div([
        dcc.Graph(figure=changing_chart),
        dcc.Graph(figure=health_chart)
    ], style={"display": "flex"})

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

import os
import re
from concurrent.futures import ProcessPoolExecutor, Future


class BatteryInfoParser:
    def __init__(self) -> None:
        pass

    @staticmethod
    def _parse_battery_cap(cap_name: str, content: str) -> int | None:
        """
        Parse battery capacity from the given contents.
        :param cap_name: Capacity name/type.
        :param content: Battery info content.
        :return: Battery capacity value, or None.
        """
        try:
            matched = re.search(pattern=fr"{cap_name}: \s*([\d.]+)\s*mAh", string=content)
            return int(matched.group(1)) if matched else None
        except re.error:
            return None

    @staticmethod
    def _parse_device_info(content: str) -> dict[str, str | int] | None:
        """
        Parse device info (brand, model, nickname, system version) from the given content.
        :param content: Battery info content.
        :return: A dictionary containing device info.
        """
        device_info = {}

        try:
            matched = re.search(pattern=r"Build fingerprint: '([^']+)'", string=content)
            if not matched:
                return None

            fingerprint = matched.group(1)
            device_info["phone_brand"] = fingerprint.split("/", 1)[0]

            details = re.search(pattern=r"([^/]+):\d+/\S+/([^:]+(?:\.[^/]+)+)(?=:)", string=fingerprint)
            if not details:
                return None

            device_info["nickname"] = details.group(1)

            raw_system_version = details.group(2)
            system_version = f"OS1.{raw_system_version.split(".", 1)[1]}" if raw_system_version.startswith(
                "V816") else raw_system_version
            device_info["system_version"] = system_version

            return device_info
        except re.error:
            return None

    @staticmethod
    def _format_time(time_str: str) -> str:
        split_time = time_str.rsplit("-", 3)
        return f"{split_time[0]} {split_time[1]}:{split_time[2]}:{split_time[3]}"

    def _parse_single_info(self, path: str) -> dict[str, str | int] | None:
        filename = os.path.basename(path)
        if not filename.startswith("bugreport") or not filename.endswith(".txt"):
            return None

        try:
            with open(file=path, mode="r", encoding="utf-8", errors="ignore") as file:
                cont = file.read()
        except (OSError, ValueError):
            return None

        raw_time = filename.split("-", 3)[-1].rsplit(".", 1)[0]
        log_capture_time = self._format_time(raw_time)

        capacity_types = [
            "Estimated battery capacity", "Last learned battery capacity",
            "Min learned battery capacity", "Max learned battery capacity"
        ]
        capacity_fields = [
            "estimated_battery_capacity", "last_learned_battery_capacity",
            "min_learned_battery_capacity", "max_learned_battery_capacity"
        ]
        database_field_name = dict(zip(capacity_types, capacity_fields))

        battery_capacities = {}

        for cap_type in capacity_types:
            battery_capacities[database_field_name[cap_type]] = self._parse_battery_cap(cap_name=cap_type, content=cont)

        device_info = self._parse_device_info(content=cont)
        parsed_data = {
            "log_capture_time": log_capture_time, **battery_capacities, **device_info
        }

        if any(parsed_data[field] is None for field in capacity_fields):
            return None

        return parsed_data

    def parse_battery_info(self, lps: list[str]) -> list[dict[str, str | int]]:
        if not isinstance(lps, list):
            raise TypeError(f"Variable 'path' must be a list, not '{type(lps).__name__}'.")

        if not lps:
            return []

        workers = min(len(lps), os.cpu_count(), 8)
        with ProcessPoolExecutor(max_workers=workers) as executor:
            futures: list[Future] = [executor.submit(self._parse_single_info, path) for path in lps]

            final_infos = []
            for future in futures:
                try:
                    result = future.result()
                    if result:
                        final_infos.append(result)
                except Exception as e:
                    print(e)
                    continue

        return final_infos


if __name__ == "__main__":
    pass

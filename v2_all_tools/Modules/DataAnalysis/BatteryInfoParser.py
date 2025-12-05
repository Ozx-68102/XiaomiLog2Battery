import os
import re
from concurrent.futures import ProcessPoolExecutor, Future

from Modules.Database import TABLE_AR_FIELDS


class BatteryInfoParser:
    def __init__(self) -> None:
        pass

    @staticmethod
    def _parse_hardware_info(content: str) -> dict[str, int] | None:
        """
        Parse hardware information from the given content.
        :param content: Battery info content.
        :return:
        """
        hardware_info = {}

        try:
            block_pattern = re.compile(
                r"^DUMP OF SERVICE android\.hardware\.health\.IHealth/default:\s*\n"
                r"(.*?)(?=^getHealthInfo -> HealthInfo\{)", re.M | re.S
            )
            block_match = re.search(pattern=block_pattern, string=content)
            if not block_match:
                return None

            target_block = block_match.group(1)
            cycle_match = re.search(pattern=r"cycle count:\s*(\d+)", string=target_block)
            if cycle_match:
                hardware_info["cycle_count"] = int(float(cycle_match.group(1)))

            capacity_match = re.search(pattern=r"Full charge:\s*(\d+)", string=target_block)
            if capacity_match:
                hardware_info["hardware_capacity"] = int(float(capacity_match.group(1)) / 1000)

            design_cap = re.search(pattern=r"batteryFullChargeDesignCapacityUah:\s*(\d+)", string=content)
            if design_cap:
                hardware_info["design_capacity"] = int(float(design_cap.group(1)) / 1000)

            return hardware_info
        except re.error:
            return None

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
            return int(float(matched.group(1))) if matched else None
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

            raw_system_version: str = details.group(2)
            system_version = (
                f"OS1.{raw_system_version.split(".", 1)[1]}"
                if raw_system_version.startswith("V816") else raw_system_version
            )
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
        capacity_fields = [field for field in TABLE_AR_FIELDS if "battery_capacity" in field]
        database_field_name = dict(zip(capacity_types, capacity_fields))

        if len(capacity_types) != len(capacity_fields):
            raise RuntimeError("The number of capacity fields from parser do not match that from database!")

        battery_capacities = {}

        for cap_type in capacity_types:
            cap_data = self._parse_battery_cap(cap_name=cap_type, content=cont)
            if cap_data:
                battery_capacities[database_field_name[cap_type]] = cap_data

        device_info = self._parse_device_info(content=cont) or {}
        hardware_info = self._parse_hardware_info(content=cont) or {}

        parsed_data = {"log_capture_time": log_capture_time, **battery_capacities, **device_info, **hardware_info}

        # Check required fields (all TABLE_AR_FIELDS are now required)
        if any(parsed_data.get(field) is None for field in TABLE_AR_FIELDS):
            return None

        return parsed_data

    def parse_battery_info(self, tps: list[str], thread_count: int) -> list[dict[str, str | int]]:
        """
        Parse battery information from the given path of files.
        :param tps: A list of paths of txt files.
        :param thread_count: Number of worker threads/processes.
        :return: A list of battery information.
        """
        if not isinstance(tps, list):
            raise TypeError(f"Variable 'lps' must be a list, not '{type(tps).__name__}'.")

        if not tps:
            return []

        if thread_count < 1:
            raise ValueError(f"Thread count must be greater than 0, current value: {thread_count}")

        # Use the provided thread count directly
        workers = min(len(tps), thread_count)

        with ProcessPoolExecutor(max_workers=workers) as executor:
            futures: list[Future] = [executor.submit(self._parse_single_info, path) for path in tps]

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

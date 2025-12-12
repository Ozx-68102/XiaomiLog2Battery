import re
from concurrent.futures import ProcessPoolExecutor, Future
from pathlib import Path

from src.config import CAPACITY_MAPPING, CAPACITY_TYPES, TABLE_FIELDS


class Parser:
    def __init__(self):
        self.cap_mapping = CAPACITY_MAPPING
        self.cap_types = CAPACITY_TYPES
        self.whole_fields = TABLE_FIELDS

    @staticmethod
    def _parse_hardware_info(string: str) -> dict[str, int] | None:
        """
        Parse hardware information from the given content.

        Parameters
        ----------
        string: str
            Battery info content.

        Returns
        -------
        dict[str, int] or None
            A dictionary with hardware information, if available.

        """
        hardware_info = {}

        try:
            block_pattern = re.compile(
                r"^DUMP OF SERVICE android\.hardware\.health\.IHealth/default:\s*\n"
                r"(.*?)(?=^getHealthInfo -> HealthInfo\{)", re.M | re.S
            )
            block_match = re.search(pattern=block_pattern, string=string)
            if not block_match:
                return None

            sub_string = block_match.group(1)
            cycle_match = re.search(pattern=r"cycle count:\s*(\d+)", string=sub_string)
            if cycle_match:
                hardware_info["cycle_count"] = int(float(cycle_match.group(1)))

            capacity_match = re.search(pattern=r"Full charge:\s*(\d+)", string=sub_string)
            if capacity_match:
                hardware_info["hardware_capacity"] = int(float(capacity_match.group(1)) / 1000)

            design_cap = re.search(pattern=r"batteryFullChargeDesignCapacityUah:\s*(\d+)", string=string)
            if design_cap:
                hardware_info["design_capacity"] = int(float(design_cap.group(1)) / 1000)

            return hardware_info

        except re.error:
            return None

    @staticmethod
    def _parse_battery_cap(cap: str, string: str) -> int | None:
        """
        Parse battery capacity from the given contents.

        Parameters
        ----------
        cap: str
            Capacity name.
        string: str
            Battery info content.

        Returns
        -------
        int or None
            Battery capacity value, if available.
        """
        try:
            matched = re.search(pattern=fr"{cap}: \s*([\d.]+)\s*mAh", string=string)
            return int(float(matched.group(1))) if matched else None
        except re.error:
            return None

    @staticmethod
    def _parse_device_info(string: str) -> dict[str, str] | None:
        """
        Parse device info (brand, model, nickname, system version) from the given content.

        Parameters
        ----------
        string: str
            Battery info content.

        Returns
        -------
        dict[str, str] or None
            A dictionary with device info.
        """
        device_info = {}

        try:
            matched = re.search(pattern=r"Build fingerprint: '([^']+)'", string=string)
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

    def _parse_info(self, path: str | Path) -> dict[str, str | int] | None:
        path = Path(path)
        filename = path.stem
        if not filename.startswith("bugreport") or not path.suffix == ".txt":
            return None

        cont = path.read_text(encoding="utf-8", errors="ignore")
        if not cont:
            return None

        raw_time = filename.split("-", 3)[-1]
        log_capture_time = self._format_time(raw_time)

        battery_cap = {}
        for cap_type in self.cap_types:
            cap_data = self._parse_battery_cap(cap=cap_type, string=cont)
            if cap_data:
                battery_cap[self.cap_mapping[cap_type]] = cap_data

        device_info = self._parse_device_info(string=cont) or {}
        hardware_info = self._parse_hardware_info(string=cont) or {}

        parsed_data = {"log_capture_time": log_capture_time, **battery_cap, **device_info, **hardware_info}

        if any(parsed_data.get(field) is None for field in self.whole_fields):
            return None

        return parsed_data

    def parser(self, tps: list[str | Path], thread_count: int) -> list[dict[str, str | int]]:
        """
        Parse battery information from the given path of files.

        Parameters
        ----------
        tps: list[str | Path]
            A list of paths of txt files.

        thread_count: int
            Number of worker threads/processes.

        Returns
        -------
        list[dict[str, str | int]]
            A list of battery information.
        """
        if not isinstance(tps, list):
            raise TypeError(f"Variable 'lps' must be a list, not '{type(tps).__name__}'.")

        if thread_count < 1:
            raise ValueError(f"Thread count must be greater than 0, current value: {thread_count}")

        if not tps:
            return []

        workers = min(len(tps), thread_count)

        with ProcessPoolExecutor(max_workers=workers) as executor:
            futures: list[Future[dict[str, str | int] | None]] = [
                executor.submit(self._parse_info, Path(path)) for path in tps
            ]

            final_info = []
            for future in futures:
                try:
                    results = future.result()
                    if results:
                        final_info.append(results)
                except Exception as e:
                    print(e)
                    continue

        return final_info


if __name__ == "__main__":
    pass

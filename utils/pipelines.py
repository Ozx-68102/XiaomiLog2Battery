import os
import shutil
from typing import Literal, Callable

from src.analysis import DataServices, Parser
from src.config import UPLOAD_PATH, TXT_PATH
from src.processing import BatteryProcessor


def _calculate_workers(mode: Literal["low", "medium", "high"], file_count: int) -> int:
    cpu_count = os.cpu_count() or 1
    if mode == "low":
        # Low mode
        return min(max(cpu_count // 2, 1), file_count, 4)

    if mode == "medium":
        # Balanced mode
        return min(max(int(cpu_count * 0.75), 1), file_count, 6)

    if mode == "high":
        # High mode
        return min(cpu_count, file_count, 8)

    raise ValueError(f"Invalid thread mode: {mode}")


def analysis_pipeline(
        mode: Literal["init", "append"],
        thread: Literal["low", "medium", "high"],
        set_progress: Callable | None = None,
) -> dict[str, str]:
    if mode not in ("init", "append"):
        raise ValueError(f"Invalid operation mode: {mode}")

    shutil.rmtree(TXT_PATH, ignore_errors=True)
    TXT_PATH.mkdir(parents=True, exist_ok=True)

    # Stage 1: Extraction
    if set_progress:
        set_progress(("10", "Phase 1/3: Extracting Zip files..."))

    zips = list(UPLOAD_PATH.glob("*.zip"))
    if not zips:
        return {"status": "error", "message": "No zip files found."}

    processor = BatteryProcessor()
    process_workers = _calculate_workers(mode=thread, file_count=len(zips))
    txt_paths = processor.process_xiaomi_log(fps=zips, thread_count=process_workers)
    if not txt_paths:
        return {"status": "error", "message": "Extraction failed. No valid log files extracted."}

    # Stage 2: Parsing Data
    if set_progress:
        set_progress(("40", f"Phase 2/3: Parsing {len(txt_paths)} logs..."))

    parser = Parser()
    parse_workers = _calculate_workers(mode=thread, file_count=len(txt_paths))
    parsed_data = parser.parser(tps=txt_paths, thread_count=parse_workers)
    if not parsed_data:
        return {"status": "error", "message": "Parsing failed. No valid battery data found in logs."}

    # Stage 3: Storing Data
    if set_progress:
        set_progress(("80", f"Phase 3/3: Saving {len(parsed_data)} records..."))

    ds = DataServices()

    if mode == "append":
        count = ds.append_data("analysis_results", parsed_data)
    else:
        count = ds.init_data("analysis_results", parsed_data)

    if set_progress:
        set_progress(("100", "Done!"))

    return {
        "status": "success",
        "message": f"Successfully processed {count} records in '{mode}' mode."
    }

import os
from typing import Literal


def _calculate_workers(mode: Literal["low", "balanced", "high"], file_count: int) -> int:
    cpu_count = os.cpu_count() or 1
    if mode == "low":
        # Low mode
        return min(max(cpu_count // 2, 1), file_count, 4)
    elif mode == "balanced":
        # Balanced mode
        return min(max(int(cpu_count * 0.75), 1), file_count, 6)
    elif mode == "high":
        # High mode
        return min(cpu_count, file_count, 8)

    raise ValueError("Invalid mode.")


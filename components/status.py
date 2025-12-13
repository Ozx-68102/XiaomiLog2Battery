from enum import StrEnum


class ProcessStatus(StrEnum):
    INIT = "init"
    SUCCESS = "success"
    ERROR = "error"


class ThreadMode(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
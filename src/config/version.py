import tomllib
from pathlib import Path


TOML_PATH = Path(__file__).parents[2] / "pyproject.toml"

def __get_project_version() -> str:
    try:
        with open(TOML_PATH, "rb") as f:
            data = tomllib.load(f)

        if "project" in data and "version" in data["project"]:
            return data["project"]["version"]
    except Exception as e:
        print(f"Warning: Could not read version from pyproject.toml: {e}")

    return "Unknown"

APP_VERSION = __get_project_version()

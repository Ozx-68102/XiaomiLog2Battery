from pathlib import Path

from .database import *
from .version import APP_VERSION

INSTANCE_PATH = Path(__file__).parents[2] / "instance"
INSTANCE_PATH.mkdir(exist_ok=True)

UPLOAD_PATH = INSTANCE_PATH / "uploads"
UPLOAD_PATH.mkdir(exist_ok=True)

DISKCACHE_PATH = INSTANCE_PATH / "cache"
TXT_PATH = INSTANCE_PATH / "extracted_txt"
DB_PATH = INSTANCE_PATH / "database.db"

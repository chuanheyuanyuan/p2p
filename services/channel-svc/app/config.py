import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

CHANNEL_DB_PATH = Path(os.environ.get('CHANNEL_DB_PATH', BASE_DIR / 'channel.db'))

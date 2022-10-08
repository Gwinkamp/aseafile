from pathlib import Path
from tests.test_data.models import Settings

SETTINGS = Settings(_env_file='.env')

BASE_DIR = Path(__file__).resolve().parent

from pathlib import Path
from aseafile_tests.test_data.models import Settings

SETTINGS = Settings(_env_file='.env')

BASE_DIR = Path(__file__).resolve().parent

from tests.config import BASE_DIR

TEST_DATA_DIR = BASE_DIR / 'test_data' / 'files'

TEST_FILES = [
    {
        'name': 'test_file_1.txt',
        'path': TEST_DATA_DIR / 'test_file_1.txt'
    },
    {
        'name': 'test_file_2.md',
        'path': TEST_DATA_DIR / 'test_file_2.md'
    },
    {
        'name': 'test_file_3.txt',
        'path': TEST_DATA_DIR / 'test_file_3.txt'
    }
]

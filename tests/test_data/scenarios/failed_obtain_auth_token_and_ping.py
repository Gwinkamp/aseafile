from tests.config import SETTINGS
from tests.test_data.context import TestContext


SCENARIOS = [
    (
        'incorrect email',
        TestContext.from_dict({
            'email': 'incorrect@fake.com',
            'password': SETTINGS.password
        })
    ),
    (
        'incorrect password',
        TestContext.from_dict({
            'email': SETTINGS.email,
            'password': 'Test123456'
        })
    ),
    (
        'incorrect email and password',
        TestContext.from_dict({
            'email': 'incorrect@fake.com',
            'password': 'Test123456'
        })
    ),
    (
        'empty password',
        TestContext.from_dict({
            'email': SETTINGS.email,
            'password': None
        })
    )
]

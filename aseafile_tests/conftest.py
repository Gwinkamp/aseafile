import pytest
import asyncio
from config import SETTINGS
from assertpy import add_extension
from collections import defaultdict
from aseafile import SeafileHttpClient
from aseafile.models import SeaResult, RepoItem
from aseafile_tests.test_logic.custom_assertions import contains_item


@pytest.fixture(scope='session')
def authorized_http_client():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()

    http_client = SeafileHttpClient(SETTINGS.base_url)
    loop.run_until_complete(http_client.authorize(SETTINGS.email, SETTINGS.password))
    return http_client


@pytest.fixture(scope='module')
def use_custom_assertions():
    add_extension(contains_item)


@pytest.fixture(scope='session')
def test_repo(authorized_http_client):
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()

    response: SeaResult[RepoItem] = loop.run_until_complete(authorized_http_client.create_repo('test'))
    if not response.success:
        raise RuntimeError('failed to create test repo')

    yield response.content.id

    loop.run_until_complete(authorized_http_client.delete_repo(response.content.id))


@pytest.fixture(scope='class')
def use_test_directory(authorized_http_client, test_repo):
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    test_dir = '/test_dir'

    response: SeaResult = loop.run_until_complete(authorized_http_client.create_directory(test_repo, test_dir))

    if not response.success:
        raise RuntimeError('failed to create test repo')

    yield

    loop.run_until_complete(authorized_http_client.delete_directory(test_repo, test_dir))


def pytest_configure(config):
    config.addinivalue_line('markers', 'incremental')


def pytest_generate_tests(metafunc):
    """Generate parameterization"""
    idlist = list()
    argvalues = list()
    try:
        if metafunc.cls.SCENARIOS is not None:
            for scenario in metafunc.cls.SCENARIOS:
                idlist.append(scenario[0])
                argvalues.append(scenario[1])
            metafunc.parametrize('context', argvalues, ids=idlist, scope="class")
    except Exception:
        pass  # skip generate parameterization


__TEST_FAILED_INCREMENTAL = defaultdict(dict)


def pytest_runtest_makereport(item, call):
    if 'incremental' in item.keywords:
        if call.excinfo is not None and call.excinfo.typename != 'Skipped':
            param = tuple(item.callspec.indices.values()) if hasattr(item, 'callspec') else ()
            __TEST_FAILED_INCREMENTAL[str(item.cls)].setdefault(
                param, item.originalname or item.name)


def pytest_runtest_setup(item):
    if 'incremental' in item.keywords:
        param = tuple(item.callspec.indices.values()
                      ) if hasattr(item, 'callspec') else ()
        originalname = __TEST_FAILED_INCREMENTAL[str(item.cls)].get(param)
        if originalname:
            pytest.xfail('previous test failed ({})'.format(originalname))

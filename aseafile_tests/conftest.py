import pytest
from collections import defaultdict


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

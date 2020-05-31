import pytest
import shutil
import os

@pytest.fixture(scope='session', autouse=True)
def create_test_module():
    os.makedirs('./tests/test_module/', exist_ok=True)


@pytest.fixture
def cleanup_locale_fixture():
    try:
        shutil.rmtree('./tests/test_module/locale')
    except OSError:
        pass
    yield


@pytest.fixture
def cleanup_fixture():
    try:
        os.remove('./tests/test_module/test_file.py')
    except OSError:
        pass
    yield


@pytest.fixture(scope='session', autouse=True)
def cleanup():
    yield
    shutil.rmtree('./tests/test_module')

import pytest
import shutil


@pytest.fixture
def cleanup_fixture():
    try:
        shutil.rmtree('./tests/test_module/locale')
    except OSError:
        pass
    yield
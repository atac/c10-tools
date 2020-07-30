
from unittest.mock import patch
import os
import sys

try:
    from i106 import C10
except ImportError:
    from chapter10 import C10

import pytest

sys.path.append('src')

SAMPLE = os.path.join(os.path.dirname(__file__), 'test', '1.c10')


def pytest_configure():
    pytest.SAMPLE = SAMPLE


@pytest.fixture
def c10():
    return C10


@pytest.fixture(scope='session')
def fake_progress():
    with patch('src.common.FileProgress'):
        yield

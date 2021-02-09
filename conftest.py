
from unittest.mock import patch
import os

try:
    from i106 import C10
except ImportError:
    from chapter10 import C10

if os.environ.get('LIBRARY', None) == 'c10':
    from chapter10 import C10

import pytest

TESTDIR = os.path.join(os.path.dirname(__file__), 'test')


def pytest_configure():
    pytest.SAMPLE = os.path.join(TESTDIR, '1.c10')
    pytest.EVENTS = os.path.join(TESTDIR, 'event.c10')
    pytest.ETHERNET = os.path.join(TESTDIR, 'ethernet.c10')


class MockC10(C10):
    def __init__(self, packets):
        self.packets = packets

    def __iter__(self):
        return iter(self.packets)


@pytest.fixture
def c10():
    return MockC10


@pytest.fixture(scope='session')
def fake_progress():
    with patch('c10_tools.common.FileProgress'):
        yield

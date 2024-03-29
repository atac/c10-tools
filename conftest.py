
from unittest.mock import patch
import os

from chapter10 import C10

import pytest

TESTDIR = os.path.join(os.path.dirname(__file__), 'tests')


def pytest_configure():
    pytest.SAMPLE = os.path.join(TESTDIR, '1.c10')
    pytest.EVENTS = os.path.join(TESTDIR, 'event.c10')
    pytest.ETHERNET = os.path.join(TESTDIR, 'ethernet.c10')
    pytest.ERR = os.path.join(TESTDIR, 'err.c10')
    pytest.BAD = os.path.join(TESTDIR, 'bad.c10')
    pytest.PCAP = os.path.join(TESTDIR, 'test.pcap')
    pytest.TMATS = os.path.join(TESTDIR, 'test.tmt')


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

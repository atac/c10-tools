
from tempfile import NamedTemporaryFile
from unittest.mock import patch
import os

try:
    from i106 import C10
except ImportError:
    from chapter10 import C10

import pytest

from src.c10_allbus import main

dirname = os.path.dirname(__file__)


@pytest.fixture(scope='module', autouse=True)
def setup_module():
    with patch('src.common.FileProgress'):
        yield


def test_overwrite():
    with NamedTemporaryFile() as out:
        with pytest.raises(SystemExit):
            main((os.path.join(dirname, '1.c10'), out.name))


def test_force():
    with NamedTemporaryFile() as out:
        main((os.path.join(dirname, '1.c10'), out.name, '-f'))
        assert os.stat(out.name).st_size > 0


def test_defaults():
    with NamedTemporaryFile() as out:
        main((os.path.join(dirname, '1.c10'), out.name, '-f'))
        for packet in C10(out.name):
            if packet.data_type == 0x19:
                for i, msg in enumerate(packet):
                    assert msg.bus == 0


def test_b():
    with NamedTemporaryFile() as out:
        main((os.path.join(dirname, '1.c10'), out.name, '-b', '-f'))
        for packet in C10(out.name):
            if packet.data_type == 0x19:
                for i, msg in enumerate(packet):
                    assert msg.bus == 1

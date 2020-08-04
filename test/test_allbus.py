
from tempfile import NamedTemporaryFile
import os

import pytest

from src.c10_allbus import main
from src.common import C10


def test_overwrite(fake_progress):
    with NamedTemporaryFile() as out:
        with pytest.raises(SystemExit):
            main((pytest.SAMPLE, out.name))


def test_force(fake_progress):
    with NamedTemporaryFile() as out:
        main((pytest.SAMPLE, out.name, '-f'))
        assert os.stat(out.name).st_size == os.stat(pytest.SAMPLE).st_size


def test_defaults(fake_progress):
    with NamedTemporaryFile() as out:
        main((pytest.SAMPLE, out.name, '-f'))
        for packet in C10(out.name):
            if packet.data_type == 0x19:
                for i, msg in enumerate(packet):
                    assert msg.bus == 0


def test_b(fake_progress):
    with NamedTemporaryFile() as out:
        main((pytest.SAMPLE, out.name, '-b', '-f'))
        for packet in C10(out.name):
            if packet.data_type == 0x19:
                for i, msg in enumerate(packet):
                    assert msg.bus == 1

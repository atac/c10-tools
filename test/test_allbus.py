
from tempfile import NamedTemporaryFile
import os

import pytest

from src.c10_allbus import main

SAMPLE = os.path.join(os.path.dirname(__file__), '1.c10')


def test_overwrite(fake_progress):
    with NamedTemporaryFile() as out:
        with pytest.raises(SystemExit):
            main((SAMPLE, out.name))


def test_force(fake_progress):
    with NamedTemporaryFile() as out:
        main((SAMPLE, out.name, '-f'))
        assert os.stat(out.name).st_size == os.stat(SAMPLE).st_size


def test_defaults(fake_progress, c10):
    with NamedTemporaryFile() as out:
        main((SAMPLE, out.name, '-f'))
        for packet in c10(out.name):
            if packet.data_type == 0x19:
                for i, msg in enumerate(packet):
                    assert msg.bus == 0


def test_b(fake_progress, c10):
    with NamedTemporaryFile() as out:
        main((SAMPLE, out.name, '-b', '-f'))
        for packet in c10(out.name):
            if packet.data_type == 0x19:
                for i, msg in enumerate(packet):
                    assert msg.bus == 1

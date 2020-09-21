
from tempfile import NamedTemporaryFile
import os

import pytest

from c10_tools.c10_allbus import main
from c10_tools.common import C10


def test_overwrite(fake_progress):
    with NamedTemporaryFile() as out:
        with pytest.raises(SystemExit):
            main((pytest.SAMPLE, out.name))


def test_force(fake_progress):
    path = NamedTemporaryFile().name
    main((pytest.SAMPLE, path, '-f'))
    assert len(list(C10(path))) == len(list(C10(pytest.SAMPLE)))


def test_defaults(fake_progress):
    path = NamedTemporaryFile().name
    main((pytest.SAMPLE, path, '-f'))
    for packet in C10(path):
        if packet.data_type == 0x19:
            for i, msg in enumerate(packet):
                assert msg.bus == 0


def test_b(fake_progress):
    path = NamedTemporaryFile().name
    main((pytest.SAMPLE, path, '-b', '-f'))
    for packet in C10(path):
        if packet.data_type == 0x19:
            for i, msg in enumerate(packet):
                assert msg.bus == 1

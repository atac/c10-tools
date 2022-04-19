
from tempfile import NamedTemporaryFile

from click.testing import CliRunner
import pytest

from c10_tools.allbus import allbus
from c10_tools.common import C10


def test_overwrite(fake_progress):
    with NamedTemporaryFile() as out:
        result = CliRunner().invoke(allbus, [pytest.SAMPLE, out.name])
        assert b'file exists' in result.stdout_bytes


def test_force(fake_progress):
    path = NamedTemporaryFile().name
    CliRunner().invoke(allbus, [pytest.SAMPLE, path, '-f'])
    assert len(list(C10(path))) == len(list(C10(pytest.SAMPLE)))


def test_defaults(fake_progress):
    path = NamedTemporaryFile().name
    CliRunner().invoke(allbus, [pytest.SAMPLE, path])
    for packet in C10(path):
        if packet.data_type == 0x19:
            for msg in packet:
                assert msg.bus == 0


def test_b(fake_progress):
    path = NamedTemporaryFile().name
    CliRunner().invoke(allbus, [pytest.SAMPLE, path, '-f', '-b'])
    for packet in C10(path):
        if packet.data_type == 0x19:
            for i, msg in enumerate(packet):
                assert msg.bus == 1

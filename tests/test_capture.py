
from tempfile import NamedTemporaryFile
import os

import pytest
from click.testing import CliRunner

from c10_tools.capture import capture


def test_overwrite():
    path = NamedTemporaryFile('wb').name
    CliRunner().invoke(capture, [pytest.PCAP, path, '-f', '-t', pytest.TMATS])
    assert os.stat(path).st_size == 7904


def test_checks_exists():
    path = NamedTemporaryFile('wb').name
    with open(path, 'w+b'):
        result = CliRunner().invoke(capture, [pytest.PCAP, path])
    assert 'file exists' in result.stdout


def test_tmats():
    path = NamedTemporaryFile('wb').name
    CliRunner().invoke(capture, [pytest.PCAP, path, '-f', '-t', pytest.TMATS])
    expected = open(pytest.TMATS, 'rb').read().replace(b'\r\n', b'\n')
    with open(path, 'rb') as f:
        assert f.read(6351)[28:] == expected
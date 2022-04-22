
from tempfile import NamedTemporaryFile

from click.testing import CliRunner
import pytest

from c10_tools.from_pcap import frompcap


@pytest.fixture
def args():
    return {
        '<infile>': pytest.PCAP,
        '<outfile>': NamedTemporaryFile().name,
        '-f': True,
        '-t': None,
        '-q': False,
    }


def test_checks_overwrite():
    with NamedTemporaryFile() as f:
        result = CliRunner().invoke(frompcap, [pytest.PCAP, f.name])
    assert 'file exists' in result.stdout


def test_default():
    path = NamedTemporaryFile().name
    CliRunner().invoke(frompcap, [pytest.PCAP, path, '-f'])


def test_tmats():
    path = NamedTemporaryFile().name
    CliRunner().invoke(frompcap, [pytest.PCAP, path, '-f', '-t', pytest.TMATS])
    assert open(path, 'rb').read(24) == b'%\xeb\x00\x00\xd0\x18\x00\x00\xb7\x18\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\xac\x1d'


from tempfile import NamedTemporaryFile

import pytest

from c10_tools.from_pcap import main


@pytest.fixture
def args():
    return {
        '<infile>': pytest.PCAP,
        '-f': True,
        '-t': None,
        '-q': False,
    }


def test_checks_overwrite(args):
    args['-f'] = False
    with NamedTemporaryFile() as out, pytest.raises(SystemExit):
        args['<outfile>'] = out.name
        main(args)


def test_default(args):
    with NamedTemporaryFile() as out:
        args['<outfile>'] = out.name
        main(args)

        
def test_tmats(args):
    args['-t'] = pytest.TMATS
    with NamedTemporaryFile() as out:
        args['<outfile>'] = out.name
        main(args)
        out.seek(0)
        assert out.read(24) == b'%\xeb\x00\x00\xd0\x18\x00\x00\xb7\x18\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\xac\x1d'

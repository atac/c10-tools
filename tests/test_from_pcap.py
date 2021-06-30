
from tempfile import NamedTemporaryFile

import pytest

from c10_tools.from_pcap import main


@pytest.fixture
def args():
    return {
        '<infile>': pytest.PCAP,
        '<outfile>': NamedTemporaryFile().name,
        '-f': True,
        '-t': None,
        '-q': False,
    }


def test_checks_overwrite(args):
    args['-f'] = False
    with NamedTemporaryFile() as f, pytest.raises(SystemExit):
        args['<outfile>'] = f.name
        main(args)


def test_default(args):
    main(args)

        
def test_tmats(args):
    args['-t'] = pytest.TMATS
    main(args)
    assert open(args['<outfile>'], 'rb').read(24) == b'%\xeb\x00\x00\xd0\x18\x00\x00\xb7\x18\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\xac\x1d'


from tempfile import NamedTemporaryFile
import os

import pytest

from c10_tools.capture import main


@pytest.fixture
def args():
    return {'<infile>': pytest.PCAP,
            '<outfile>': NamedTemporaryFile('wb').name,
            '-f': True,
            '-q': True,
            '-t': pytest.TMATS}


def test_overwrite(args):
    main(args)
    assert os.stat(args['<outfile>']).st_size == 7904


def test_checks_exists(args):
    args['-f'] = False
    with open(args['<outfile>'], 'w+b'), pytest.raises(SystemExit):
        main(args)


def test_tmats(args):
    args['-t'] = pytest.TMATS
    main(args)
    expected = open(pytest.TMATS, 'rb').read().replace(b'\r\n', b'\n')
    with open(args['<outfile>'], 'rb') as f:
        assert f.read(6351)[28:] == expected 
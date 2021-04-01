
from tempfile import NamedTemporaryFile
from datetime import timedelta
from unittest.mock import patch
from io import BytesIO
import os

import pytest

from c10_tools.copy import main
from c10_tools.common import C10


@pytest.fixture
def args():
    return {'<src>': pytest.ETHERNET,
            '<dst>': NamedTemporaryFile().name,
            '--force': True}


ETHERNET = open(pytest.ETHERNET, 'rb').read()
SAMPLE = open(pytest.SAMPLE, 'rb').read()


def fake_open(path, mode):
    if path == pytest.ETHERNET:
        return BytesIO(ETHERNET)
    if path == pytest.SAMPLE:
        return BytesIO(SAMPLE)
    return open(path, mode)


def test_overwrite(args):
    args['<src>'] = pytest.SAMPLE
    main(args)
    assert os.stat(args['<dst>']).st_size == \
        os.stat(pytest.SAMPLE).st_size


def test_checks_exists(args):
    args['--force'] = False
    with patch('c10_tools.copy.open', fake_open):
        with open(args['<dst>'], 'w+b'), pytest.raises(SystemExit):
            main(args)


def test_trim_abs(args):
    args['<end>'] = '290:22:19:23'
    with open(args['<dst>'], 'w+b') as out:
        main(args)
        out.seek(0)
        packets = list(C10(args['<dst>']))
        assert str(packets[-1].get_time()) == '2018-10-17 22:19:22.998157'


def test_trim_rel(args):
    args['<end>'] = '0:02'
    with open(args['<dst>'], 'w+b') as out:
        main(args)
        out.seek(0)
        packets = list(C10(args['<dst>']))
        assert packets[-1].get_time() - packets[1].time < timedelta(seconds=2)


def test_trim_offset(args):
    args['<end>'] = '10000'
    with open(args['<dst>'], 'w+b'):
        main(args)
        assert os.stat(args['<dst>']).st_size < 10_000


def test_slice_abs(args):
    args['<start>'] = '290:22:19:23'
    args['<end>'] = '290:22:19:24'
    with open(args['<dst>'], 'w+b') as out:
        main(args)
        out.seek(0)
        packets = list(C10(args['<dst>']))
        assert str(packets[1].time) == '2018-10-17 22:19:22'
        assert str(packets[-1].get_time()) == '2018-10-17 22:19:23.988158'


def test_slice_abs_rel(args):
    args['<start>'] = '290:22:19:23'
    args['<end>'] = '0:01'
    with open(args['<dst>'], 'w+b') as out:
        main(args)
        out.seek(0)
        packets = list(C10(args['<dst>']))
        assert str(packets[1].time) == '2018-10-17 22:19:22'
        assert str(packets[-1].get_time()) == '2018-10-17 22:19:23.988158'


def test_slice_abs_offset(args):
    args['<start>'] = '290:22:19:23'
    args['<end>'] = '100000'
    with open(args['<dst>'], 'w+b'):
        main(args)
        assert os.stat(args['<dst>']).st_size < 100_000


def test_slice_rel(args):
    args['<start>'] = '0:01'
    args['<end>'] = '0:02'
    with open(args['<dst>'], 'w+b') as out:
        main(args)
        out.seek(0)
        packets = list(C10(args['<dst>']))
        assert str(packets[1].time) == '2018-10-17 22:19:23'
        assert str(packets[-1].get_time()) == '2018-10-17 22:19:24.988158'


def test_slice_rel_abs(args):
    args['<start>'] = '0:01'
    args['<end>'] = '290:22:19:24.988158'
    with open(args['<dst>'], 'w+b') as out:
        main(args)
        out.seek(0)
        packets = list(C10(args['<dst>']))
        assert str(packets[1].time) == '2018-10-17 22:19:23'
        assert str(packets[-1].get_time()) == '2018-10-17 22:19:24.971918'


def test_slice_rel_offset(args):
    args['<start>'] = '0:01'
    args['<end>'] = '1000000'
    with open(args['<dst>'], 'w+b') as out:
        main(args)
        out.seek(0)
        packets = list(C10(args['<dst>']))
        assert str(packets[1].time) == '2018-10-17 22:19:23'
        assert os.stat(args['<dst>']).st_size == 749960


def test_slice_offset(args):
    args['<start>'] = '1000'
    args['<end>'] = '1000000'
    with open(args['<dst>'], 'w+b'):
        main(args)
        assert os.stat(args['<dst>']).st_size <= 1_000_000


def test_slice_offset_abs(args):
    args['<start>'] = '1000'
    args['<end>'] = '290:22:19:24.988158'
    with open(args['<dst>'], 'w+b') as out:
        main(args)
        out.seek(0)
        packets = list(C10(args['<dst>']))
        assert str(packets[0].time) == '2018-10-17 22:19:22'
        assert str(packets[-1].get_time()) == '2018-10-17 22:19:24.971918'


def test_slice_offset_rel(args):
    args['<start>'] = '1000'
    args['<end>'] = '0:01'
    with open(args['<dst>'], 'w+b') as out:
        main(args)
        out.seek(0)
        packets = list(C10(args['<dst>']))
        assert str(packets[0].time) == '2018-10-17 22:19:22'
        assert str(packets[-1].get_time()) == '2018-10-17 22:19:22.998157'

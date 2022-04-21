
from tempfile import NamedTemporaryFile
from datetime import timedelta
import os

from click.testing import CliRunner
import pytest

from c10_tools.copy import copy
from c10_tools.common import C10


def test_overwrite():
    path = NamedTemporaryFile().name
    CliRunner().invoke(copy, [pytest.SAMPLE, path, '-f'])
    assert os.stat(path).st_size == \
        os.stat(pytest.SAMPLE).st_size


def test_checks_exists():
    path = NamedTemporaryFile().name
    with open(path, 'w+b'):
        result = CliRunner().invoke(copy, [pytest.SAMPLE, path])
    assert 'file already exists' in result.stdout


def test_trim_abs():
    path = NamedTemporaryFile().name
    with open(path, 'w+b') as f:
        CliRunner().invoke(copy, [pytest.ETHERNET, path, '0', '290:22:19:23', '-f'])
        packets = list(C10(f))
    assert str(packets[-1].get_time()) == '2018-10-17 22:19:22.998157'


def test_trim_rel():
    path = NamedTemporaryFile().name
    with open(path, 'w+b') as out:
        CliRunner().invoke(copy, [pytest.ETHERNET, path, '0', '0:02', '-f'])
        packets = list(C10(out))
        assert packets[-1].get_time() - packets[1].time < timedelta(seconds=2)


def test_trim_offset():
    path = NamedTemporaryFile().name
    with open(path, 'w+b'):
        CliRunner().invoke(copy, [pytest.ETHERNET, path, '0', '10000', '-f'])
        assert os.stat(path).st_size < 10_000


def test_slice_abs():
    path = NamedTemporaryFile().name
    CliRunner().invoke(copy, [pytest.ETHERNET, path, '290:22:19:23', '290:22:19:24', '-f'])
    packets = list(C10(path))
    assert str(packets[1].time) == '2018-10-17 22:19:23'
    assert str(packets[-1].get_time()) == '2018-10-17 22:19:23.988158'


def test_slice_abs_rel():
    path = NamedTemporaryFile().name
    CliRunner().invoke(copy, [pytest.ETHERNET, path, '290:22:19:23', '0:01', '-f'])
    packets = list(C10(path))
    assert str(packets[1].time) == '2018-10-17 22:19:23'
    assert str(packets[-1].get_time()) == '2018-10-17 22:19:23.988158'


def test_slice_abs_offset():
    path = NamedTemporaryFile().name
    CliRunner().invoke(copy, [pytest.ETHERNET, path, '290:22:19:23', '100000', '-f'])
    assert os.stat(path).st_size < 100_000


def test_slice_rel():
    path = NamedTemporaryFile().name
    CliRunner().invoke(copy, [pytest.ETHERNET, path, '0:01', '0:02', '-f'])
    packets = list(C10(path))
    assert str(packets[1].time) == '2018-10-17 22:19:23'
    assert str(packets[-1].get_time()) == '2018-10-17 22:19:24.988158'


def test_slice_rel_abs():
    path = NamedTemporaryFile().name
    CliRunner().invoke(copy, [pytest.ETHERNET, path, '0:01', '290:22:19:24.988158', '-f'])
    packets = list(C10(path))
    assert str(packets[1].time) == '2018-10-17 22:19:23'
    assert str(packets[-1].get_time()) == '2018-10-17 22:19:24.971918'


def test_slice_rel_offset():
    path = NamedTemporaryFile().name
    CliRunner().invoke(copy, [pytest.ETHERNET, path, '0:01', '1000000', '-f'])
    packets = list(C10(path))
    assert str(packets[1].time) == '2018-10-17 22:19:23'
    assert os.stat(path).st_size == 749960


def test_slice_offset():
    path = NamedTemporaryFile().name
    CliRunner().invoke(copy, [pytest.ETHERNET, path, '1000', '1000000', '-f'])
    assert os.stat(path).st_size <= 1_000_000


def test_slice_offset_abs():
    path = NamedTemporaryFile().name
    CliRunner().invoke(copy, [pytest.ETHERNET, path, '1000', '290:22:19:24.988158', '-f'])
    packets = list(C10(path))
    assert str(packets[0].time) == '2018-10-17 22:19:22'
    assert str(packets[-1].get_time()) == '2018-10-17 22:19:24.971918'


def test_slice_offset_rel():
    path = NamedTemporaryFile().name
    CliRunner().invoke(copy, [pytest.ETHERNET, path, '1000', '0:01', '-f'])
    packets = list(C10(path))
    assert str(packets[0].time) == '2018-10-17 22:19:22'
    assert str(packets[-1].get_time()) == '2018-10-17 22:19:22.998157'

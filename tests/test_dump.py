
from contextlib import redirect_stdout
from datetime import datetime
from io import BytesIO

from click.testing import CliRunner
import pytest

from c10_tools.dump import dump


@pytest.fixture
def args():
    return {'<file>': pytest.SAMPLE,
            '<channel>': '2',
            '--pcap': False,
            '--binary': False,
            '--byteoffset': 0,
            '--count': None}


@pytest.fixture
def stdout():
    class tmp:
        buffer = BytesIO()

        @staticmethod
        def isatty():
            return True

        @staticmethod
        def flush():
            pass

    return tmp


def test_hex():
    expected = [
        '{}-12-09 16:47:12.359557 9e 10 fa 3f eb',
        '{}-12-09 16:47:12.360211 80 11 00 60 c4',
        '{}-12-09 16:47:12.375214 bc 10 3e ff e0',
        '{}-12-09 16:47:12.375828 5e 11 3f 70 00',
        '{}-12-09 16:47:12.389436 24 14 00 10 00',
        '{}-12-09 16:47:12.389570 84 31 84 15 00',
        '{}-12-09 16:47:12.389749 a4 31 a4 15 00',
        '{}-12-09 16:47:12.406162 40 14 00 10 fe',
        '{}-12-09 16:47:12.406856 6e 14 00 10 c4',
        '{}-12-09 16:47:12.407190 cf 10 00 70 00',
        '{}-12-09 16:47:12.407544 ff 10 fd ff 00',
        '{}-12-09 16:47:12.422134 1e 11 f3 03 00',
        '{}-12-09 16:47:12.436558 2d 10 00 fe c6',
        '{}-12-09 16:47:12.452759 5d 10 e7 ef 34',
        '{}-12-09 16:47:12.453393 39 11 fe ff 18',
        '{}-12-09 16:47:12.453948 c9 30 c9 14 00',
        '{}-12-09 16:47:12.454226 e9 30 e9 14 00',
        '{}-12-09 16:47:12.454504 84 31 84 15 00',
        '{}-12-09 16:47:12.454683 a4 31 a4 15 00',
        '{}-12-09 16:47:12.468084 7f 10 ec ff 90',
        '{}-12-09 16:47:12.468758 67 11 00 22 00',
        '{}-12-09 16:47:12.468952 40 14 00 10 fe',
        '{}-12-09 16:47:12.483979 20 40 00 00 00',
        '{}-12-09 16:47:12.484665 9e 10 fa 3f eb',
        '{}-12-09 16:47:12.485319 80 11 00 60 c4',
        '{}-12-09 16:47:12.500432 bc 10 3e ff e0',
        '{}-12-09 16:47:12.501046 5e 11 3f 70 00',
        '{}-12-09 16:47:12.514530 24 14 00 10 00',
        '{}-12-09 16:47:12.514664 84 31 84 15 00',
        '{}-12-09 16:47:12.514843 a4 31 a4 15 00',
        '{}-12-09 16:47:12.530965 40 14 00 10 fe',
        '{}-12-09 16:47:12.531659 6e 14 00 10 c4',
        '{}-12-09 16:47:12.531993 cf 10 00 70 00',
        '{}-12-09 16:47:12.532347 ff 10 fd ff 10',
        '{}-12-09 16:47:12.546774 1e 11 f3 03 00',
        '{}-12-09 16:47:12.561297 2d 10 00 fe c6',
        '{}-12-09 16:47:12.577660 5d 10 e7 ef 34',
        '{}-12-09 16:47:12.578294 39 11 fe ff 18',
        '{}-12-09 16:47:12.578848 84 31 84 15 00',
        '{}-12-09 16:47:12.579027 a4 31 a4 15 00',
        '{}-12-09 16:47:12.592956 7f 10 ec ff 90',
        '{}-12-09 16:47:12.593630 67 11 00 22 00',
        '{}-12-09 16:47:12.593824 40 14 00 10 fe',
        '{}-12-09 16:47:12.609068 20 40 00 00 00',
        '{}-12-09 16:47:12.609754 9e 10 fa 3f eb',
        '{}-12-09 16:47:12.610408 80 11 00 60 c4',
        '{}-12-09 16:47:12.611102 3c 31 3c 15 00']
    year = str(datetime.now().year)
    expected = '\n'.join([row.format(year) for row in expected])
    result = CliRunner().invoke(dump, [pytest.SAMPLE, '2', '--count', '5'])
    result = result.stdout.strip().replace('\r\n', '\n').replace('\r', '\n')
    assert result.endswith(expected)


def test_pcap():
    result = CliRunner().invoke(dump, [pytest.ETHERNET, '30', '--pcap'])
    assert b'\xd4\xc3\xb2\xa1\x02\x00\x04\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\xdc\x05\x00\x00\x01\x00\x00\x00' in result.stdout_bytes


def test_bin():
    result = CliRunner().invoke(dump, [pytest.SAMPLE, '2', '--bin'])
    expected =  b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x9e\x10\xfa?\xeb\xff\xc5\xb2\x00\x00\x04\x00\x93F\xc8\xb8\x00\x01\x80~\x9f\x0f\xa4o\x00p\x03n\x03n\x00\x00\x00\x00\x00\x8e\xc0\xc3\x00\x00\x00P\x00P\x00P\x00\x8e\xc0\xc3\xe0.\x002\x00}\x00\x00@M\x00Z\x00\x10\x80\x11\x00`\xc43\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    assert expected in result.stdout_bytes
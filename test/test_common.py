
from unittest.mock import Mock
import os

import pytest

from c10_tools import common


def test_find_c10():
    dirname = os.path.dirname(__file__)
    result = common.find_c10([dirname])
    assert set(result) == set([pytest.SAMPLE, pytest.EVENTS])


def test_fmt_table():
    result = common.fmt_table([('1 2 3', 'hello', 'world'),
                               ('One', '1', '1.0'),
                               ('Two', '2', '2.1'),
                               ('Three', '3', '3.0')])
    assert result == '''-------------------------
| 1 2 3 | hello | world |
-------------------------
| One   |     1 | 1.0   |
| Two   |     2 | 2.1   |
| Three |     3 | 3.0   |
-------------------------'''


packets = [
    Mock(channel_id=0, data_type=0),
    Mock(channel_id=12, data_type=2),
    Mock(channel_id=5, data_type=15),
]


def test_walk_packets_noargs(c10):
    assert list(common.walk_packets(c10(packets))) == packets


def test_walk_packets_include_channel(c10):
    result = common.walk_packets(c10(packets), {'--channel': '0'})
    assert list(result) == [packets[0]]


def test_walk_packets_exclude_channel(c10):
    result = common.walk_packets(c10(packets), {'--exclude': '12'})
    assert list(result) == [packets[0], packets[2]]


def test_walk_packets_include_type(c10):
    result = common.walk_packets(c10(packets), {'--type': '2'})
    assert list(result) == packets[:2]

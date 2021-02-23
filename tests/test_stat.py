
import os

import pytest

from c10_tools import stat as c10_stat

expected = '''
---------------------------------------------------------------------------
| Channel ID | Data Type                            | Packets | Size      |
---------------------------------------------------------------------------
| Channel  0 | 0x01 - Computer Generated (format 1) |       1 |   6.52 kb |
| Channel  1 | 0x11 - Time (format 1)               |       1 |     36  b |
| Channel  2 | 0x19 - Mil-STD-1553 (format 1)       |       3 |   2.93 kb |
| Channel  3 | 0x19 - Mil-STD-1553 (format 1)       |       3 |    9.2 kb |
| Channel  4 | 0x19 - Mil-STD-1553 (format 1)       |       3 |   7.77 kb |
| Channel  5 | 0x19 - Mil-STD-1553 (format 1)       |       3 |   8.36 kb |
| Channel  6 | 0x38 - ARINC 429 (format 0)          |       3 |   6.51 kb |
| Channel  7 | 0x38 - ARINC 429 (format 0)          |       3 |   7.51 kb |
| Channel  8 | 0x38 - ARINC 429 (format 0)          |       3 |    8.1 kb |
| Channel  9 | 0x38 - ARINC 429 (format 0)          |       3 |   3.05 kb |
| Channel 10 | 0x38 - ARINC 429 (format 0)          |       3 |   5.45 kb |
| Channel 11 | 0x38 - ARINC 429 (format 0)          |       3 |   7.93 kb |
| Channel 12 | 0x30 - Message (format 0)            |       6 |  73.38 kb |
| Channel 13 | 0x40 - Video (format 0)              |       8 | 122.16 kb |
| Channel 14 | 0x40 - Video (format 0)              |       7 | 106.89 kb |
| Channel 15 | 0x40 - Video (format 0)              |       7 | 106.89 kb |
| Channel 16 | 0x40 - Video (format 0)              |       7 | 106.89 kb |
| Channel 17 | 0x40 - Video (format 0)              |       7 | 106.89 kb |
| Channel 18 | 0x40 - Video (format 0)              |       7 | 106.89 kb |
| Channel 19 | 0x40 - Video (format 0)              |       7 | 106.89 kb |
| Channel 20 | 0x40 - Video (format 0)              |       7 | 106.89 kb |
---------------------------------------------------------------------------
Summary for {}:
    Channels:                21     Start time:        343-2021 16:47:12
    Packets:                 95     End time:          343-2021 16:47:12
    Size:            1017.11 kb     Duration:             0:00:00.472549
    '''.format(os.path.abspath(pytest.SAMPLE)).strip()


def test_single(fake_progress):
    assert '\n'.join(
        list(c10_stat.main({'<file>': [pytest.SAMPLE]}))).strip() == expected


def test_multiple(fake_progress):
    result = '\n'.join(list(c10_stat.main(
        {'<file>': [pytest.SAMPLE, pytest.SAMPLE, pytest.SAMPLE]})))
    assert result.strip() == '\n\n'.join([expected, expected, expected])

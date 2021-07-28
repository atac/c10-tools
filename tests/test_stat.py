
import os

import pytest

from c10_tools import stat as c10_stat

expected = '''
---------------------------------------------------------------------------
| Channel ID | Data Type                            | Packets | Size      |
---------------------------------------------------------------------------
| Channel  0 | 0x01 - Computer Generated (format 1) |       1 |   6.52 kb |
| Channel  1 | 0x11 - Time (format 1)               |       2 |     72  b |
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
    Channels:                21     Start time:             343 16:47:12
    Packets:                 96     End time:               343 16:47:12
    Size:            1017.14 kb     Duration:             0:00:00.472549
'''.format(os.path.abspath(pytest.SAMPLE)).strip()


def test_single(fake_progress):
    result = '\n'.join(
        list(c10_stat.main({'<file>': [pytest.SAMPLE],
                            '--verbose': False}))).strip()
    assert result == expected


def test_multiple(fake_progress):
    result = '\n'.join(list(c10_stat.main(
        {'<file>': [pytest.SAMPLE, pytest.SAMPLE, pytest.SAMPLE],
         '--verbose': False})))
    assert result.strip() == '\n\n'.join([expected, expected, expected])


def test_verbose_1553(fake_progress):
    result = '\n'.join(list(c10_stat.main(
        {'<file>': [pytest.ERR],
         '--verbose': True,
         '--channel': '2',
         })))
    assert result == '''
--------------------------------------------------------------------
| Channel ID | Data Type                      | Packets | Size     |
--------------------------------------------------------------------
| Channel  1 | 0x11 - Time (format 1)         |       2 |    72  b |
| Channel  2 | 0x19 - Mil-STD-1553 (format 1) |      25 | 76.66 kb |
|   Command words (41):                                            |
|     0061                                                         |
|     0062                                                         |
|     0be2                                                         |
|     0ccb                                                         |
|     1f63                                                         |
|     2060                                                         |
|     2062                                                         |
|     2578                                                         |
|     2ecc                                                         |
|     3d61                                                         |
|     3f7c                                                         |
|     4060                                                         |
|     4061                                                         |
|     4062                                                         |
|     4b7c                                                         |
|     50c8                                                         |
|     6060                                                         |
|     6061                                                         |
|     77c8                                                         |
|     8060                                                         |
|     8061                                                         |
|     8467                                                         |
|     8563                                                         |
|     8de7                                                         |
|     a060                                                         |
|     a061                                                         |
|     a062                                                         |
|     a4cb                                                         |
|     a563                                                         |
|     c061                                                         |
|     c062                                                         |
|     c27b                                                         |
|     c27f                                                         |
|     c2cb                                                         |
|     c2cf                                                         |
|     c2e3                                                         |
|     c2e7                                                         |
|     df60                                                         |
|     e060                                                         |
|     e061                                                         |
|     e062                                                         |
--------------------------------------------------------------------
Summary for {}:
    Channels:                 2     Start time:             132 20:05:00
    Packets:                 27     End time:               132 20:05:01
    Size:              76.73 kb     Duration:             0:00:01.391045
'''.format(os.path.abspath(pytest.ERR)).lstrip()


def test_verbose_event(fake_progress):
    result = '\n'.join(list(c10_stat.main(
        {'<file>': [pytest.EVENTS],
         '--verbose': True})))
    assert result == '''
------------------------------------------------------------------------
| Channel ID | Data Type                            | Packets | Size   |
------------------------------------------------------------------------
| Channel  0 | 0x02 - Computer Generated (format 2) |       7 | 308  b |
|   Events:                                                            |
|        2:          1                                                 |
|      258:          1                                                 |
|      514:          1                                                 |
|      770:          1                                                 |
|     1026:          1                                                 |
|     1282:          1                                                 |
|     1538:          1                                                 |
------------------------------------------------------------------------
Summary for {}:
    Channels:                 1     Start time:                        0
    Packets:                  7     End time:                          0
    Size:                308  b     Duration:                          0
'''.format(os.path.abspath(pytest.EVENTS)).lstrip()

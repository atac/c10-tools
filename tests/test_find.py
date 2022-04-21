
from click.testing import CliRunner
import pytest

from c10_tools.find import find


def test_find_simple():
    result = CliRunner().invoke(find, ['0x00', '--offset', '2', pytest.SAMPLE])
    assert '''00   at 606820
    00   at 606836
    00   at 606844
    00   at 606852
    00   at 606916
    00   at 606940
    00   at 607052
    00   at 607060
    00   at 607084
    00   at 607124''' in result.stdout


def test_find_channel():
    result = CliRunner().invoke(find, ['0x00', '--offset', '2', '--channel', '2', pytest.SAMPLE])
    assert result.stdout.startswith('Searching for 0x0 in channel #2 at offset 2 in 1 files...')
    assert result.stdout.strip().endswith(f'''
    00  343 16:47:12.358870 at 136800
    00  343 16:47:12.360210 at 136958
    00  343 16:47:12.389436 at 137192
    00  343 16:47:12.406162 at 137278
    00  343 16:47:12.406856 at 137360
    00  343 16:47:12.407190 at 137406
    00  343 16:47:12.436557 at 137612
    00  343 16:47:12.468758 at 547376
    00  343 16:47:12.468952 at 547408
    00  343 16:47:12.483978 at 547490
    00  343 16:47:12.485319 at 547648
    00  343 16:47:12.514530 at 547882
    00  343 16:47:12.530965 at 547968
    00  343 16:47:12.531659 at 548050
    00  343 16:47:12.531992 at 548096
    00  343 16:47:12.561296 at 900666
    00  343 16:47:12.593630 at 900994
    00  343 16:47:12.593824 at 901026
    00  343 16:47:12.609067 at 901108
    00  343 16:47:12.610408 at 901266

finished''')


def test_find_command():
    result = CliRunner().invoke(find, ['*', '--cmd', '0x109e', '--offset', '2', pytest.SAMPLE])
    assert result.stdout == '''Searching for * with command word 0x109e at offset 2 in 1 files...

  {}
    fa  343 16:47:12.359556 at 136880
    fa  343 16:47:12.484665 at 547570
    fa  343 16:47:12.609754 at 901188

finished\n'''.format(pytest.SAMPLE)

def test_find_mask():
    result = CliRunner().invoke(find, ['0xf', '--mask', '0x0f', '--channel', '2', '--offset', '2', pytest.SAMPLE])
    assert result.stdout == '''Searching for 0xf in channel #2 at offset 2 with mask 15 in 1 files...

  {}
    0f  343 16:47:12.375828 at 137114
    0f  343 16:47:12.501045 at 547804

finished\n'''.format(pytest.SAMPLE)


def test_find_all():
    result = CliRunner().invoke(find, ['*', '--offset', '2', pytest.SAMPLE])
    assert '''5e  343 16:47:12.650318 at 1025246
    5e  343 16:47:12.653069 at 1025436
    5e  343 16:47:12.653521 at 1025538
    5e  343 16:47:12.654233 at 1025614
    16   at 1025912
    17   at 1026100
    18   at 1026288''' in result.stdout
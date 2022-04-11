
from unittest.mock import patch

from termcolor import colored
import pytest

from c10_tools.inspect import main


@pytest.fixture
def args():
    return {
        '<file>': [pytest.SAMPLE],
        '--quiet': False,
    }


def test_defaults_csv(args, capsys):
    for i, line in enumerate(main(args)):
        if i == 5:
            break
    result = capsys.readouterr().out
    assert result == 'Channel,Type,Sequence,Size,Time,Valid,Offset0,1,182,6680,N/A,Yes,01,17,110,36,343 16:47:12.000000,Yes,66803,25,204,3168,343 16:47:12.347833,Yes,671610,56,102,1800,343 16:47:12.347336,Yes,988413,64,196,15636,343 16:47:12.254091,Yes,11684' 
    

def test_defaults_ascii(args):
    result = []
    with patch('csv.writer', return_value=None):
        for i, line in enumerate(main(args)):
            result.append(line)
            if i == 5:
                break
    assert '\n'.join(result) == '''\
-----------------------------------------------------------------------------------------------
| Channel | Type | Sequence | Size    | Time                        | Valid | Offset          |
-----------------------------------------------------------------------------------------------
|       0 |    1 |      182 |   6,680 | N/A                         | Yes   |               0 |
|       1 |   17 |      110 |      36 | 343 16:47:12.000000         | Yes   |           6,680 |
|       3 |   25 |      204 |   3,168 | 343 16:47:12.347833         | Yes   |           6,716 |
|      10 |   56 |      102 |   1,800 | 343 16:47:12.347336         | Yes   |           9,884 |
|      13 |   64 |      196 |  15,636 | 343 16:47:12.254091         | Yes   |          11,684 |'''


def test_error_csv(args):
    args['<file>'] = [pytest.BAD]
    args['--channel'] = '1'
    result = list(main(args))
    assert result == ['', '', '"Type 0x5 not implemented at 36"']


def test_error_ascii(args):
    args['<file>'] = [pytest.BAD]
    result = []
    with patch('csv.writer', return_value=None):
        for i, line in enumerate(main(args)):
            result.append(line)
            if i == 5:
                break
    print('\n'.join(result))
    assert '\n'.join(result) == '''\
-----------------------------------------------------------------------------------------------
| Channel | Type | Sequence | Size    | Time                        | Valid | Offset          |
-----------------------------------------------------------------------------------------------
|       0 |    1 |      182 |   6,680 | N/A                         | Yes   |               0 |
|       1 |   17 |      110 |      36 | 343 16:47:12.000000         | Yes   |           6,680 |
{}
|      14 |   64 |      196 |  15,636 | 343 16:47:12.254729         | Yes   |          24,182 |
|      18 |   64 |      195 |  15,636 | 343 16:47:12.255114         | Yes   |          39,818 |'''.format(
    colored('Packet length incorrect at 6,716', 'red'))


def test_inspect_filtering(args):
    type_counts = [
        (1, 2),
        (17, 2),
        (25, 13),
        (48, 7),
        (56, 19),
        (64, 58),
    ]
    args['<file>'] = [pytest.SAMPLE]
    for typ, expected in type_counts:
        args['--type'] = str(typ)
        result = list(main(args))
        assert len(result) == expected

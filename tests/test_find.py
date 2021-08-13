
import pytest

from c10_tools.find import main


@pytest.fixture
def args():
    return {
        '<value>': '0x3ffa',
        '<path>': (pytest.SAMPLE,),
        '--channel': None,
        '--offset': '2',
        '--mask': None,
        '--length': '2',
    }


def test_search_simple(args, capsys):
    main(args)
    result = capsys.readouterr().out
    assert result == '''Searching for 0x3ffa at offset 2 in 1 files...

  {}
    3ffa  343 16:47:12.359556 at 136880
    3ffa  343 16:47:12.484665 at 547570
    3ffa  343 16:47:12.609754 at 901188

finished\n'''.format(pytest.SAMPLE)


def test_search_channel(args, capsys):
    return
    # args['--channel'] = '2'
    args['<value>'] = '0x00'
    args['--offset'] = '2'
    main(args)
    result = capsys.readouterr().out
    # print(result)
    # assert 0
    assert result == '''Searching for 0x3ffa at offset 2 in 1 files...

  {}
    343 16:47:12.359556    137660
    343 16:47:12.484665    548228
    343 16:47:12.609754    901432

finished\n'''.format(pytest.SAMPLE)

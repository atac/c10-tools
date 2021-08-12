
import pytest

from c10_tools.grep import main


@pytest.fixture
def args():
    return {
        '<value>': '0x3ffa',
        '<path>': (pytest.SAMPLE,),
        '--channel': None,
        '--offset': '0',
        '--mask': None,
        '--length': '1',
    }


def test_search_simple(args, capsys):
    main(args)
    result = capsys.readouterr().out
    assert result == '''Searching for 0x3ffa at offset 2 in 1 files...

  {}
    343 16:47:12.359556    137660
    343 16:47:12.484665    548228
    343 16:47:12.609754    901432

finished\n'''.format(pytest.SAMPLE)


def test_search_channel(args, capsys):
    # args['--channel'] = '2'
    args['<value>'] = '0x00'
    args['--offset'] = '2'
    main(args)
    result = capsys.readouterr().out
    print(result)
    assert 0
    assert result == '''Searching for 0x3ffa at offset 2 in 1 files...

  {}
    343 16:47:12.359556    137660
    343 16:47:12.484665    548228
    343 16:47:12.609754    901432

finished\n'''.format(pytest.SAMPLE)
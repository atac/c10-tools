
import docopt
import pytest

from c10_tools import c10_stat


def test_noargs(fake_progress):
    with pytest.raises(docopt.DocoptExit):
        c10_stat.main([])


def test_single(fake_progress):
    c10_stat.main([pytest.SAMPLE])


# def test_multiple(fake_progress):
#     c10_stat.main([pytest.SAMPLE, pytest.SAMPLE, pytest.SAMPLE])

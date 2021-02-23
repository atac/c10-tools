
import pytest
import docopt

from c10_tools import c10_errcount


def test_noargs():
    with pytest.raises(docopt.DocoptExit):
        c10_errcount.main([])


def test_default():
    c10_errcount.main([pytest.SAMPLE])

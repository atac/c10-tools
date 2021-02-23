
import pytest

import docopt

from c10_tools import c10_dmp1553


def test_noargs():
    with pytest.raises(docopt.DocoptExit):
        c10_dmp1553.main()


def test_sanity(c10):
    c10_dmp1553.main([pytest.SAMPLE, '100'])

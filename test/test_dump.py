
from tempfile import TemporaryDirectory

import pytest
import docopt

from src import c10_dump


def test_noargs():
    with pytest.raises(docopt.DocoptExit):
        c10_dump.main()


# Segfaults with i106
# def test_sanity(c10):
#     with TemporaryDirectory() as out:
#         c10_dump.main([pytest.SAMPLE, '-o', out])

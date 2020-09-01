
from tempfile import NamedTemporaryFile

import pytest
import docopt

from c10_tools.c10_reindex import Parser


def test_noargs():
    with pytest.raises(docopt.DocoptExit):
        Parser().main([])


def test_default():
    path = NamedTemporaryFile().name
    Parser([pytest.SAMPLE, path, '-f']).main()

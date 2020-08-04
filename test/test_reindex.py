
from tempfile import NamedTemporaryFile

import pytest
import docopt

from src.c10_reindex import Parser


def test_noargs():
    with pytest.raises(docopt.DocoptExit):
        Parser().main()


def test_default():
    with NamedTemporaryFile() as out:
        Parser([pytest.SAMPLE, out.name, '-f']).main()


from tempfile import NamedTemporaryFile

import pytest
import docopt

from c10_tools.c10_timefix import main


def test_noargs():
    with pytest.raises(docopt.DocoptExit):
        main([])


def test_default():
    path = NamedTemporaryFile().name
    main([pytest.SAMPLE, path])

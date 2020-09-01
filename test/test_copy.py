
from tempfile import NamedTemporaryFile
import os

import pytest

from c10_tools.c10_copy import main


SOURCE = os.path.join(os.path.dirname(__file__), '1.c10')


def test_overwrite():
    with NamedTemporaryFile() as out:
        with pytest.raises(SystemExit):
            main((SOURCE, out.name))


def test_noargs():
    path = NamedTemporaryFile().name
    with open(path, 'w+b') as out:
        main((SOURCE, path, '-f'))
        out.seek(0)
        assert out.read() == open(SOURCE, 'rb').read()

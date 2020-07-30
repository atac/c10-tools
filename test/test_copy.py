
from tempfile import NamedTemporaryFile
import os

import pytest

from src.c10_copy import main


SOURCE = os.path.join(os.path.dirname(__file__), '1.c10')


def test_overwrite():
    with NamedTemporaryFile() as out:
        with pytest.raises(SystemExit):
            main((SOURCE, out.name))


def test_noargs():
    with NamedTemporaryFile('w+b') as out:
        main((SOURCE, out.name, '-f'))
        out.seek(0)
        assert out.read() == open(SOURCE, 'rb').read()

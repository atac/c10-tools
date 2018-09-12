
from tempfile import NamedTemporaryFile
import os

import pytest

from src.c10_copy import main


dirname = os.path.dirname(__file__)
src = os.path.join(dirname, '1.c10')


def test_overwrite():
    with NamedTemporaryFile() as out:
        with pytest.raises(SystemExit):
            main((os.path.join(dirname, '1.c10'), out.name))


def test_noargs():
    with NamedTemporaryFile('w+b') as out:
        main((src, out.name, '-f'))
        out.seek(0)
        assert out.read() == open(src, 'rb').read()

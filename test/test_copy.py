
from tempfile import NamedTemporaryFile

import pytest

from c10_tools.c10_copy import wrapper as main


def test_overwrite():
    with NamedTemporaryFile() as out:
        with pytest.raises(SystemExit):
            main((pytest.SOURCE, out.name))


def test_noargs():
    path = NamedTemporaryFile().name
    with open(path, 'w+b') as out:
        main((pytest.SOURCE, path, '-f'))
        out.seek(0)
        assert out.read() == open(pytest.SOURCE, 'rb').read()

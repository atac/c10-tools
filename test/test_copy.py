
from tempfile import NamedTemporaryFile

import pytest

from c10_tools.copy import wrapper as main


def test_overwrite():
    with NamedTemporaryFile() as out:
        with pytest.raises(SystemExit):
            main((pytest.SAMPLE, out.name))


def test_noargs():
    path = NamedTemporaryFile().name
    with open(path, 'w+b') as out:
        main((pytest.SAMPLE, path, '-f'))
        out.seek(0)
        assert out.read() == open(pytest.SAMPLE, 'rb').read()

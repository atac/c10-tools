
from tempfile import NamedTemporaryFile

from click.testing import CliRunner
import pytest

from c10_tools.timefix import timefix


def test_default():
    path = NamedTemporaryFile().name
    CliRunner().invoke(timefix, [pytest.SAMPLE, path], obj={'quiet': True})
    assert open(pytest.SAMPLE, 'rb').read() == open(path, 'rb').read()
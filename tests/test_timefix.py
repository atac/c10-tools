
from tempfile import NamedTemporaryFile

import pytest

from c10_tools.timefix import main


@pytest.fixture
def args():
    return {
        '<input_file>': pytest.SAMPLE,
        '<output_file>': NamedTemporaryFile().name,
        '--quiet': True,
        '--force': True,
    }


def test_default(args):
    main(args)
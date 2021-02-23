
from tempfile import NamedTemporaryFile

import pytest

from c10_tools.allbus import main
from c10_tools.common import C10


def test_overwrite(fake_progress):
    with NamedTemporaryFile() as out:
        with pytest.raises(SystemExit):
            main({'<src>': pytest.SAMPLE,
                  '<dst>': out.name,
                  '--force': False})


def test_force(fake_progress):
    path = NamedTemporaryFile().name
    main({'<src>': pytest.SAMPLE,
          '<dst>': path,
          '--force': True,
          '-b': 0})
    assert len(list(C10(path))) == len(list(C10(pytest.SAMPLE)))


def test_defaults(fake_progress):
    path = NamedTemporaryFile().name
    main({'<src>': pytest.SAMPLE,
          '<dst>': path,
          '--force': True,
          '-b': 0})
    for packet in C10(path):
        if packet.data_type == 0x19:
            for i, msg in enumerate(packet):
                assert msg.bus == 0


def test_b(fake_progress):
    path = NamedTemporaryFile().name
    main({'<src>': pytest.SAMPLE,
          '<dst>': path,
          '--force': True,
          '-b': 1})
    for packet in C10(path):
        if packet.data_type == 0x19:
            for i, msg in enumerate(packet):
                assert msg.bus == 1

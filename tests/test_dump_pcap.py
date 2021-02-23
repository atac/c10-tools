
from tempfile import TemporaryDirectory

from c10_tools.c10_dump_pcap import main
import pytest


def test_defaults():
    with TemporaryDirectory() as out:
        main([pytest.ETHERNET, out + '/tmp.pcap', '30'])

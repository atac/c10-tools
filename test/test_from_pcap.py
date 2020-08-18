
from tempfile import NamedTemporaryFile

import pytest
import docopt

from c10_tools.c10_from_pcap import PCAPParser


def test_noargs():
    with pytest.raises(docopt.DocoptExit):
        PCAPParser().main()


def test_default():
    with NamedTemporaryFile() as out:
        PCAPParser([pytest.SAMPLE, out.name]).main()

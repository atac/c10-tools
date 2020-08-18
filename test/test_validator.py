
import pytest
import docopt

from c10_tools.c10_validator import Parser


def test_noargs():
    with pytest.raises(docopt.DocoptExit):
        Parser().main()


def test_default():
    Parser([pytest.SAMPLE]).main()

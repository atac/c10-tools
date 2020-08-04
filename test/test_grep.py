
import pytest
import docopt

from src.c10_grep import main


def test_noargs():
    with pytest.raises(docopt.DocoptExit):
        main()


def test_default():
    main(['*', pytest.SAMPLE])

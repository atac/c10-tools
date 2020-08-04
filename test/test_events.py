
from datetime import datetime

import pytest
import docopt

from src import c10_events


def test_noargs():
    with pytest.raises(docopt.DocoptExit):
        c10_events.main()


def test_default(c10):
    c10_events.main([pytest.EVENTS])

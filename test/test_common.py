
import os

from src import common


def test_find_c10():
    dirname = os.path.dirname(__file__)
    result = common.find_c10([dirname])
    assert list(result) == [os.path.join(dirname, '1.c10')]

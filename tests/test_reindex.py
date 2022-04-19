
from tempfile import NamedTemporaryFile

from chapter10 import C10
from click.testing import CliRunner
import pytest

from c10_tools.reindex import reindex


def test_root_offsets():
    path = NamedTemporaryFile().name
    CliRunner().invoke(reindex, [pytest.SAMPLE, path, '-f'])
    with open(path, 'rb') as f:
        packets = list(C10(f))
        offsets = list(packets[-1])
        assert len(offsets) == 2
        for node in offsets:
            f.seek(node.offset)
            assert next(C10(f)).data_type == 0x3


def test_node_offsets():
    path = NamedTemporaryFile().name
    CliRunner().invoke(reindex, [pytest.SAMPLE, path, '-f'])
    with open(path, 'rb') as f:
        for packet in C10(f):
            if packet.data_type == 0x3 and packet.index_type == 1:
                indices = [(index.offset, index.channel_id, index.data_type)
                           for index in packet]
                break
        for offset, channel_id, data_type in indices:
            f.seek(offset)
            packet = next(C10(f))
            assert (packet.channel_id, packet.data_type) == (channel_id, data_type)


from tempfile import NamedTemporaryFile

from chapter10 import C10
from chapter10.computer import ComputerF3
import pytest

from c10_tools.reindex import main


@pytest.fixture
def args():
    return {
        '<src>': pytest.SAMPLE,
        '<dst>': NamedTemporaryFile().name,
        '--strip': False,
        '--force': True,
        '--quiet': False,
    }


def test_root_offsets(args):
    main(args)
    with open(args['<dst>'], 'rb') as f:
        packets = list(C10(f))
        offsets = list(packets[-1])
        assert len(offsets) == 2
        for node in offsets:
            f.seek(node.offset)
            assert next(C10(f)).data_type == 0x3
            

def test_node_offsets(args):
    main(args)
    with open(args['<dst>'], 'rb') as f:
        for packet in C10(f):
            if packet.data_type == 0x3 and packet.index_type == 1:
                indices = [(index.offset, index.channel_id, index.data_type)
                           for index in packet]
                break
        for offset, channel_id, data_type in indices:
            f.seek(offset)
            packet = next(C10(f))
            assert (packet.channel_id, packet.data_type) == (channel_id, data_type)

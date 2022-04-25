from cgi import test
from cmath import exp
import os

from bitstruct import pack, unpack
import pytest

from c10_tools.broadcast import UDPTransferHeaderFormat3

########################################################
#               build test bytearray                   #
########################################################

offset_to_packet_start    = 0     # 16 bits
reserved                  = 0     # 8 bits
source_id_length          = 2     # 4 bit field - Don't change value
format                    = 3     # 4 bit field
source_id                 = 5     # feild length of src_id_len*4  (4-bit nibbles)
datagram_sequence_number  = 0     # field length = 32 - (src_id_len*4)

@pytest.fixture
def test_bytes():
    return pack('u16u8u4u4u8u24',
                offset_to_packet_start,
                reserved,
                source_id_length,
                format,
                source_id,
                datagram_sequence_number
                )

@pytest.fixture
def expected_from_bytes():
    return (0,0,2,3,5,0)

########################################################
#                     begin tests                      #
########################################################

def test_test_bytes(expected_from_bytes, test_bytes):
    assert expected_from_bytes == unpack('u16u8u4u4u8u24',test_bytes)


def test_get_header_bytes(test_bytes):
    header = UDPTransferHeaderFormat3(0, 5, 0, 2)
    assert test_bytes == header.get_header_bytes()


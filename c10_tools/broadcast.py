
import socket
import os

from chapter10 import C10
import dpkt
from numpy import broadcast

from bitstruct import pack

from c10_tools.common import FileProgress


class UDPTransferHeaderFormat3:
    """IRIG 106, Chapter 10, Section 10.3.9.1.5 Format 3, UDP Transfer Header

    args = (datagram_seq_number : int,
            src_id :int,
            off_to_packet_start: int,
            src_id_len :int = 2)
    """
    def __int__(self, datagram_seq_number : int, src_id :int,
                    off_to_packet_start: int, src_id_len :int = 2):

        self.offset_to_packet_start =  off_to_packet_start  # 16 bits
        self.reserved = 0                                   # 8 bits
        self.src_id_len= src_id_len                         # 4 bit field
        self.format = 3                                     # 4 bit field
        self.src_id = src_id                                # feild length of src_id_len*4  (4-bit nibbles)
        self.datagram_sequence_number = datagram_seq_number # field length = 32 - (src_id_len*4)


    def get_header_bytes(self) -> bytearray:
        """Returns the information stored in UDP Transfer Header as an 8 bytes field.\n
        Little Endian byte ordering is used.
        """
        header      = bytearray(self.offset_to_packet_start.to_bytes(2,'little'))
        header.append(self.reserved.to_bytes(1,'little'))

        # build bytes from two nibbles
        bit_field   = pack('u4u4', self.src_id_len, self.format)
        header.append(bit_field)

        # build bytes from variable number of nibbles per field
        bit_field   = pack('u{}u{}'.format(self.src_id_len*4, 32-self.src_id_len*4),
                            self.src_id, self.datagram_sequence_number)
        header.append(bit_field)

        return header


class NetworkBroadcast:
    """Broadcast chapter 10 file from input file"""
    BUFF_SIZE = 1024  # UDP payload size = 65507
    RECORDER_TCP_PORT_DEFUALT = 10620

    def __init__(self, args=[]):
        self.args = args
        self.buf = b''
        self.ch10_file = args['<infile>']
        self.dest_ip = args['-d'].split(':')[0]
        self.dest_port = args['-d'].split(':')[1]

    def chunck_ch10(self):
        """Provides chunks of ch10 file to be transmitted."""
        # If UDP, use Format 3 header from IRIG 106, Chapter 10,
        # Section 10.9.3


        # If TCP, no header according to IRIG 106, Chapter 10,
        # Section 10.9.3.2

        # Using TCP/IP, Chapter 11 packets are transmitted in the
        # exact same format (byte for byte) as they would be written
        # to local storage media.
        pass

    def broadcast_TCP(self):
        """Transmit file chunks using TCP, following IRIG106, Chapter 10,
        section 10.3.9.2"""

        pass

    def broadcast_UDP(self):
        """Transmit file chuncks using UDP"""
        UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

        # for chunck in chapter10 file
        for i in range(100):
            chunk = b'ABCDEFGH'
            UDPServerSocket.sendto(chunk, (self.dest_ip, self.dest_port))


    def main(self):
        """Transmit or broadcast a chapter10 file over network."""

        safe = input("Type 'safe' to verify input file is safe to broadcast: ")
        if safe.strip().strip("'").lower() == "safe":
            print("Input file not verified to be safe for broadcast.")
            raise SystemExit

        # check args
        # check protocal flags=
        # start
        print("Input file valid")


def main(args):
    """Broadcast chapter 10 file over the network.
    broadcast -p <infile> -d <destination-address:port> [options]
    -s <source-address:port>
    -s  <UDP or TCP> - default setting is UDP
    -r  broadcast on repeat (loop).
    -q  Don't display progress bar.
    -t <tmats_file>  Insert an existing TMATS record at the beginning of the\
broadcast.
    """

    if not os.path.exists(args['<infile>']):
        print('Input file does not exist. Check path.')
        raise SystemExit

    broadcaster = broadcast(args)
    broadcaster.main()


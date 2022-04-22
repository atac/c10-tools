
from chapter10 import C10
import dpkt

from c10_tools.common import FileProgress


class NetworkBroadcast:
    """Broadcast chapter 10 file from input file"""
    BUFF_SIZE = 65535  # IPv4 and UDP packet size

    def __init__(self, args=[]):
        self.args = args
        self.buf = b''
        self.ch10_file = args[0]



    def main(self):
        """Transmit or broadcast a chapter10 file over network."""

        # ask user to varify that file is safe to transmit (input: safe = continue)

        # check args

        # check protocal flags

        # start
        pass


def main(args):
    """Broadcast chapter 10 file over the network.
    broadcast -p <infile> <source-address> <destination-address> [options]
    -protocol-flag {UDP or TCP} - default TCP
    -s  IPv4 style source address and port number e.g. 127.0.0.1:10202
    -d  IPv4 style destination adddress
    -q  Don't display progress bar.
    -t <tmats_file>  Insert an existing TMATS record at the beginning of the\
broadcast.
    """
    pass





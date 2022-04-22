
import socket
import os

from chapter10 import C10
import dpkt
from numpy import broadcast

from c10_tools.common import FileProgress


class NetworkBroadcast:
    """Broadcast chapter 10 file from input file"""
    BUFF_SIZE = 1024  # UDP payload size = 65507

    def __init__(self, args=[]):
        self.args = args
        self.buf = b''
        self.ch10_file = args['<infile>']
        self.dest_ip = args['-d'].split(':')[0]
        self.dest_port = args['-d'].split(':')[1]

    def chunck_ch10(self):
        """Provides chunks of ch10 file to be transmitted"""
        # first implement chunck based on buffer size,
        # can implement chunk based on packet(s) size
        # relative to buffer later
        pass

    def broadcast_TCP(self):
        """Transmit file chunks using TCP"""
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

        # ask user to varify that file is safe to transmit (input: safe = continue)
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


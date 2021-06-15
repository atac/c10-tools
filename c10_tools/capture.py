#!/usr/bin/env python

from array import array
from contextlib import suppress
import os
import struct
import sys

from chapter10 import C10
from chapter10.computer import ComputerF1
from termcolor import colored
from docopt import docopt
import dpkt

from c10_tools.common import FileProgress, fmt_number


def wrapper(argv=sys.argv[1:]):
    print(colored('This will be deprecated in favor of c10 capture', 'red'))
    args = docopt('''Extract chapter 10 data from a pcap file.

usage: c10-from-pcap <infile> <outfile> [options]

Options:
    -q               Don't display progress bar.
    -f               Overwrite existing output file.
    -t <tmats_file>  Insert an existing TMATS record at the beginning of the\
output file.
''')
    return main(args)


class PCAPParser:
    BUF_SIZE = 100000
    buf = b''

    def __init__(self, args=[]):
        self.args = args

    def parse(self, data, out_file):
        """Take a string of bytes and attempt to parse chapter 10 data."""

        packets_added = 0

        # Limit the buffer size and add new data to the buffer.
        self.buf = self.buf[-self.BUF_SIZE:] + data

        for i in range(self.buf.count(b'\x25\xeb')):
            sync = self.buf.find(b'\x25\xeb')
            if sync < 0:
                continue

            with suppress(RuntimeError, EOFError):
                for packet in C10.from_string(self.buf[sync:]):
                    raw = bytes(packet)
                    if len(raw) == packet.packet_length:
                        packets_added += 1
                        out_file.write(raw)

                    # Only read one packet.
                    break

            self.buf = self.buf[sync + 2:]

        return packets_added

    def main(self):
        """Parse a pcap file into chapter 10 format."""

        if os.path.exists(self.args['<outfile>']) and not self.args['-f']:
            print('Output file exists. Use -f to overwrite.')
            raise SystemExit

        with open(self.args['<outfile>'], 'wb') as out:

            # Write TMATS.
            if self.args['-t']:
                with open(self.args['-t'], 'r') as tmats:
                    tmats_body = tmats.read()
                tmats = ComputerF1(data_type=1, data=tmats_body)
                out.write(bytes(tmats))

            # Loop over the packets and parse into C10.Packet objects if
            # possible.
            packets, added = 0, 0

            with open(self.args['<infile>'], 'rb') as f, \
                    FileProgress(self.args['<infile>']) as progress:

                if self.args['-q']:
                    progress.close()

                for packet in dpkt.pcap.Reader(f):
                    ip = dpkt.ethernet.Ethernet(packet[1]).data
                    if hasattr(ip, 'data') and isinstance(
                            ip.data, dpkt.udp.UDP):
                        data = ip.data.data[4:]
                        packets += 1
                        added += self.parse(data, out)

                    # Update progress bar.
                    progress.update_from_tell(f.tell())

            if not self.args['-q']:
                print('Parsed %s Chapter 10 packets from %s network packets'
                      % (fmt_number(added), fmt_number(packets)))
                

def main(args):
    """Capture chapter 10 data from a pcap file.
    capture <infile> <outfile> [options]
    -q  Don't display progress bar.
    -f  Overwrite existing output file.
    -t <tmats_file>  Insert an existing TMATS record at the beginning of the\
output file.
    """

    parser = PCAPParser(args)
    parser.main()

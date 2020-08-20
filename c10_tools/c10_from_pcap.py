#!/usr/bin/env python

"""Extract chapter 10 data from a pcap file.

usage: c10-from-pcap <infile> <outfile> [options]

Options:
    -q               Don't display progress bar.
    -f               Overwrite existing output file.
    -t <tmats_file>  Insert an existing TMATS record at the beginning of the\
output file.
"""

from array import array
from contextlib import suppress
import os
import struct
import sys

from chapter10 import C10
from docopt import docopt
import dpkt

from c10_tools.common import FileProgress, fmt_number


class PCAPParser:
    BUF_SIZE = 100000
    buf = b''

    def __init__(self, args=[]):
        self.args = docopt(__doc__, args)

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
            return

        with open(self.args['<outfile>'], 'wb') as out:

            # Write TMATS.
            if self.args['-t']:
                with open(self.args['<tmats_file>'], 'r') as tmats:
                    tmats_body = tmats.read()

                header_values = [
                    0xeb25,
                    0,
                    len(tmats_body) + 24,
                    len(tmats_body),
                    0,
                    0,
                    0,
                    1,
                    0,
                    0,
                ]

                header = struct.pack('HHIIBBBBIH', *header_values)
                out.write(header)

                # Compute and append checksum.
                sums = sum(array('H', header)) & 0xffff
                out.write(struct.pack('H', sums))

                out.write(tmats_body)

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


def main():
    parser = PCAPParser(sys.argv[1:])
    parser.main()


if __name__ == '__main__':
    main()

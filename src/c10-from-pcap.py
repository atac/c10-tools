#!/usr/bin/env python

"""Extract chapter10 data from a pcap file.

usage: c10-from-pcap <infile> <outfile> [options]

Options:
    -q               Don't display progress bar.
    -f               Overwrite existing output file.
    -t <tmats_file>  Insert an existing TMATS record at the beginning of the\
output file.
"""

from array import array
from contextlib import suppress
from datetime import datetime
import os
import struct

from i106 import C10
from docopt import docopt
import dpkt

from common import FileProgress, fmt_number


BUF_SIZE = 100000
buf = b''


def parse(data, out_file):
    """Take a string of bytes and attempt to parse chapter 10 data into db."""

    global buf

    packets_added = 0

    # Limit the buffer size and add new data to the buffer.
    buf = buf[-BUF_SIZE:] + data

    for i in range(buf.count(b'\x25\xeb')):
        sync = buf.find(b'\x25\xeb')
        if sync < 0:
            continue

        with suppress(RuntimeError):
            for packet in C10(buffer=buf[sync:]):
                raw = bytes(packet)
                if len(raw) == packet.packet_length:
                    packets_added += 1
                    out_file.write(raw)

                # Only read one packet.
                break

        buf = buf[sync + 2:]

    return packets_added


def main():
    """Parse a pcap file into chapter 10 format."""

    args = docopt(__doc__)

    if os.path.exists(args['<outfile>']) and not args['-f']:
        print('Output file exists. Use -f to overwrite.')
        return

    with open(args['<outfile>'], 'wb') as out:

        # Write TMATS.
        if args['-t']:
            with open(args['<tmats_file>'], 'r') as tmats:
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

        # Loop over the packets and parse into C10.Packet objects if possible.
        packets, added = 0, 0

        with open(args['<infile>'], 'rb') as f, \
                FileProgress(args['<infile>']) as progress:

            if args['-q']:
                progress.close()

            for packet in dpkt.pcap.Reader(f):
                ip = dpkt.ethernet.Ethernet(packet[1]).data
                if hasattr(ip, 'data') and isinstance(
                        ip.data, dpkt.udp.UDP):
                    data = ip.data.data[4:]
                    packets += 1
                    added += parse(data, out)

                # Update progress bar.
                progress.update_from_tell(f.tell())

        if not args['-q']:
            print('Parsed %s Chapter 10 packets from %s network packets' % (
                fmt_number(added), fmt_number(packets)))


if __name__ == '__main__':
    main()

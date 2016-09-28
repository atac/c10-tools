#!/usr/bin/env python

"""Parse a pcap file and print chapter10 data found within to stdout.

usage: pcap2c10 <infile> <outfile> [options]

Options:
    -q               Don't display progress bar.
    -f               Overwrite existing output file.
    -t <tmats_file>  Insert an existing TMATS record at the beginning of the output file.
"""

from array import array
import struct
import os

from chapter10 import Packet
from docopt import docopt
import dpkt

from common import FileProgress, fmt_number


BUF_SIZE = 100000
buf = ''


def parse(data, out_file):
    """Take a string of bytes and attempt to parse chapter 10 data into db."""

    global buf

    packets_added = 0

    # Limit the buffer size and add new data to the buffer.
    buf = buf[-BUF_SIZE:] + data

    for i in range(buf.count('\x25\xeb')):

        sync = buf.find('\x25\xeb')
        if sync < 0:
            break

        try:
            packet = Packet.from_string(buf[sync:], True)
        except (EOFError, OverflowError):
            break

        if len(bytes(packet)) == packet.packet_length and packet.check():
            packets_added += 1
            buf = buf[sync + packet.packet_length:]
            out_file.write(bytes(packet))

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

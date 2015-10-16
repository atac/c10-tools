#!/usr/bin/env python

'''usage: pcap2c10 <infile> <outfile> [-t <tmats_file>]

Parse a pcap file and print chapter10 data found within to stdout.
Optionally insert a TMATS packet from <tmats_file> at the beginning.
'''

from array import array
from cStringIO import StringIO
import struct

# Suppress scapy import warnings.
import logging
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)

from chapter10 import C10
from docopt import docopt
from scapy.all import rdpcap
from scapy.layers.inet import UDP


def main():
    """Parse a pcap file into chapter 10 format."""

    args = docopt(__doc__)

    packets = rdpcap(args['<infile>'])

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
        for eth in packets:
            if not hasattr(eth, 'payload'):
                continue
            if isinstance(eth.payload.payload, UDP):
                eth_packet = str(eth.load[4:])
                for p in C10(StringIO(eth_packet)):
                    out.write(bytes(p))

if __name__ == '__main__':
    main()

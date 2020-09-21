#!/usr/bin/env python

"""usage: c10-reindex <src> <dst> [options]

Options:
    -s, --strip  Strip existing index packets and exit.
    -f, --force  Overwrite existing files.
"""

from io import BytesIO
from array import array
import os
import struct
import sys

from docopt import docopt

from c10_tools.common import FileProgress, C10


class Parser:
    # Sequence number for channel 0
    seq = 0

    def __init__(self, args=[]):
        self.args = docopt(__doc__, args)

    def header(self, data_length, rtc):
        packet = bytes()

        rtc_low = int((rtc >> 32) & 0xffffffff)
        rtc_high = int((rtc >> 16) & 0xffff)

        values = [0xeb25,
                  0,
                  24 + data_length,
                  data_length,
                  0x06,
                  self.seq,
                  0,
                  0x03,
                  rtc_low,
                  rtc_high]

        # Increment sequence.
        self.seq += 1
        self.seq &= 0xff

        # Compute checksum
        sums = sum(array('H', struct.pack('=HHIIBBBBIH', *values))) & 0xffff
        values.append(sums)
        packet += struct.pack('=HHIIBBBBIHH', *values)

        return packet

    def gen_node(self, packets):
        """Generate an index node packet."""

        packet = self.header(12 + (20 * len(packets)), packets[-1].rtc)

        # CSDW
        packet += struct.pack('=I', int(1 << 31) | int(1 << 30) | len(packets))

        # File Length (at start of node, doubles as node packet offset)
        pos = packets[-1].offset + packets[-1].packet_length
        packet += struct.pack('=Q', pos)

        # Packets
        for p in packets:
            packet += struct.pack('=Q', p.rtc)
            packet += struct.pack('=xBHQ', p.data_type, p.channel_id, p.offset)

        return pos, packet

    def gen_root(self, nodes, last, last_packet):
        """Generate a root index packet."""

        pos = last_packet.offset + last_packet.packet_length

        # Root offset (as last message)
        if last is None:
            last = pos
        nodes.append(last)

        packet = self.header(12 + (16 * len(nodes)), last_packet.rtc)

        # CSDW
        packet += struct.pack('=I', int(1 << 30) | len(nodes))

        # File Length (at start of node)
        packet += struct.pack('=Q', pos)

        # Node Offsets (and a root offset)
        for node in nodes:
            packet += struct.pack('=QQ', last_packet.rtc, node)

        return pos, packet

    def main(self):
        # Don't overwrite unless explicitly required.
        if os.path.exists(self.args['<dst>']) and not self.args['--force']:
            print('Destination file already exists. Use -f to overwrite.')
            raise SystemExit

        with open(self.args['<dst>'], 'wb') as out, \
                FileProgress(self.args['<src>']) as progress:

            # Data packets, node index packets
            packets, nodes = [], []
            last_packet, last_root = None, None

            for packet in C10(self.args['<src>']):
                progress.update(packet.packet_length)

                # Skip old index packets.
                if packet.data_type == 0x03:
                    continue
                elif packet.channel_id == 0:
                    self.seq = packet.sequence_number

                last_packet = packet

                # Write data to output file.
                raw = bytes(packet)
                if len(raw) == packet.packet_length:
                    out.write(raw)

                # Just stripping existing indices so move along.
                if self.args['--strip']:
                    continue

                # Note packet position in the output file.
                packet.offset = out.tell() - packet.packet_length
                packets.append(packet)

                # Projected index node packet size.
                size = 36 + (20 * len(packets))

                # Write index if we run across a recording index or time
                # packet.
                if packet.data_type in (0x02, 0x11) or size > 524000:
                    offset, raw = self.gen_node(packets)
                    nodes.append(offset)
                    out.write(raw)
                    packets = []

                # Write root index if needed.
                if (44 + (16 * len(nodes))) > 524000:
                    last_root, raw = self.gen_root(
                        nodes, last_root, last_packet)
                    out.write(raw)
                    nodes = []

            # Final indices.
            if packets:
                offset, raw = self.gen_node(packets)
                nodes.append(offset)
                out.write(raw)
                try:
                    batch = C10(BytesIO(raw))
                except TypeError:
                    batch = C10(buffer=raw)
                for packet in batch:
                    last_packet = packet
                    break
                last_packet.offset = out.tell() - last_packet.packet_length
            if nodes:
                offset, raw = self.gen_root(nodes, last_root, last_packet)
                out.write(raw)

        if self.args['--strip']:
            print('Stripped existing indices.')


def main():
    Parser(sys.argv[1:]).main()


if __name__ == '__main__':
    main()

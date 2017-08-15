#!/usr/bin/env python

"""usage: c10-reindex <src> <dst> [options]

Options:
    -s, --strip  Strip existing index packets and exit.
    -f, --force  Overwrite existing files.
"""

from array import array
import os
import struct

from docopt import docopt

from chapter10 import C10, Packet
from chapter10.datatypes import Computer
from common import FileProgress


# Sequence number for channel 0
seq = 0


def header(data_length, rtc):
    global seq

    packet = bytes()

    values = [0xeb25,
              0,
              24 + data_length,
              data_length,
              0x06,
              seq,
              0,
              0x03,
              rtc[0],
              rtc[1]]

    # Increment sequence.
    seq += 1
    seq &= 0xff

    # Compute checksum
    sums = sum(array('H', struct.pack('=HHIIBBBBIH', *values))) & 0xffff
    values.append(sums)
    packet += struct.pack('=HHIIBBBBIHH', *values)

    return packet


def gen_node(packets):
    """Generate an index node packet."""

    packet = header(12 + (20 * len(packets)),
                    (packets[-1].rtc_low, packets[-1].rtc_high))

    # CSDW
    packet += struct.pack('=I', int(1 << 31) | int(1 << 30) | len(packets))

    # File Length (at start of node, doubles as node packet offset)
    pos = packets[-1].pos + packets[-1].packet_length
    packet += struct.pack('=Q', pos)

    # Packets
    for p in packets:
        packet += struct.pack('=II', p.rtc_low & 0xffff, p.rtc_high & 0xffff)
        packet += struct.pack('=xBHQ', p.data_type, p.channel_id, p.pos)

    return pos, packet


def gen_root(nodes, last, last_packet):
    """Generate a root index packet."""

    pos = last_packet.pos + last_packet.packet_length

    # Root offset (as last message)
    if last is None:
        last = pos
    nodes.append(last)

    packet = header(12 + (16 * len(nodes)),
                    (last_packet.rtc_low, last_packet.rtc_high))

    # CSDW
    packet += struct.pack('=I', int(1 << 30) | len(nodes))

    # File Length (at start of node)
    packet += struct.pack('=Q', pos)

    # Node Offsets (and a root offset)
    for node in nodes:
        packet += struct.pack('=II', last_packet.rtc_low & 0xffff,
                              last_packet.rtc_high & 0xffff)
        packet += struct.pack('=Q', node)

    return pos, packet


if __name__ == '__main__':
    args = docopt(__doc__)

    # Don't overwrite unless explicitly required.
    if os.path.exists(args['<dst>']) and not args['--force']:
        print('Destination file already exists. Use -f to overwrite.')
        raise SystemExit

    with open(args['<dst>'], 'wb') as out, \
            FileProgress(args['<src>']) as progress:

        # Data packets, node index packets
        packets, nodes = [], []
        last_packet, last_root = None, None

        for packet in C10(args['<src>']):
            progress.update(packet.packet_length)

            # Skip old index packets.
            if packet.data_type == 0x03:
                continue
            elif isinstance(packet.body, Computer):
                seq = packet.sequence_number

            last_packet = packet

            # Write data to output file.
            raw = bytes(packet)
            if len(raw) == packet.packet_length:
                out.write(raw)

            # Just stripping existing indices so move along.
            if args['--strip']:
                continue

            # Note packet position in the output file.
            packet.pos = out.tell() - packet.packet_length
            packets.append(packet)

            # Projected index node packet size.
            size = 36 + (20 * len(packets))

            # Write index if we run across a recording index or time packet.
            if packet.data_type in (0x02, 0x11) or size > 524000:
                offset, raw = gen_node(packets)
                nodes.append(offset)
                out.write(raw)
                packets = []

            # Write root index if needed.
            if (44 + (16 * len(nodes))) > 524000:
                last_root, raw = gen_root(nodes, last_root, last_packet)
                out.write(raw)
                nodes = []

        # Final indices.
        if packets:
            offset, raw = gen_node(packets)
            nodes.append(offset)
            out.write(raw)
            last_packet = Packet.from_string(raw)
            last_packet.pos = out.tell() - last_packet.packet_length
        if nodes:
            offset, raw = gen_root(nodes, last_root, last_packet)
            out.write(raw)

    if args['--strip']:
        print('Stripped existing indices.')

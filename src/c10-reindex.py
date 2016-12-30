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

from chapter10 import C10
from common import walk_packets


def gen_node(packets, seq=0):
    """Generate an index node packet."""

    print ('Index node for %s packets' % len(packets))

    packet = bytes()

    # Header
    values = [0xeb25,
              0,
              24 + 4 + 8 + (20 * len(packets)),
              4 + 8 + (20 * len(packets)),
              0x06,
              seq,
              0,
              0x03,
              packets[-1].rtc_low,
              packets[-1].rtc_high]

    sums = struct.pack('HHIIBBBBIH', *values)
    sums = sum(array('H', sums)) & 0xffff
    values.append(sums)
    packet += struct.pack('HHIIBBBBIHH', *values)

    # CSDW
    csdw = 0x0000
    csdw &= 1 << 31
    csdw &= 1 << 30
    csdw += len(packets)
    packet += struct.pack('I', csdw)

    # File Length (at start of node)
    pos = packets[-1].pos + packets[-1].packet_length
    packet += struct.pack('Q', pos)

    # Packets
    for p in packets:
        ipts = struct.pack('HH', p.rtc_low & 0xffff, p.rtc_high & 0xffff)
        index = struct.pack('xHHQ', p.channel_id, p.data_type, p.pos)
        packet += ipts + index

    return pos, packet


def gen_root(nodes, last, seq, last_packet):
    """Generate a root index packet."""

    print ('Root index for: %s nodes' % len(nodes))

    packet = bytes()

    # Header
    values = [0xeb25,
              0,
              24 + 4 + 8 + 8 + (16 * len(packets)),
              4 + 8 + 8 + (16 * len(packets)),
              0x06,
              seq,
              0,
              0x03,
              last_packet.rtc_low,
              last_packet.rtc_high]

    sums = struct.pack('HHIIBBBBIH', *values)
    sums = sum(array('H', sums)) & 0xffff
    values.append(sums)
    packet += struct.pack('HHIIBBBBIHH', *values)

    # CSDW
    csdw = 0x0000
    csdw &= 1 << 30
    csdw += len(nodes)
    packet += struct.pack('I', csdw)

    # File Length (at start of node)
    pos = last_packet.pos + last_packet.packet_length
    packet += struct.pack('Q', pos)

    # Node Packets
    for node in nodes:
        ipts = struct.pack('HH', last_packet.rtc_low & 0xffff,
                           last_packet.rtc_high & 0xffff)
        offset = struct.pack('Q', pos - node)
        packet += ipts + offset

    if last is None:
        last = last_packet.pos + last_packet.packet_length
    packet += struct.pack('Q', last)

    return pos, packet


def increment(seq):
    """Increment the sequence number or reset it."""

    seq += 1
    if seq > 0xFF:
        seq = 0
    return seq


if __name__ == '__main__':
    args = docopt(__doc__)

    # Don't overwrite unless explicitly required.
    if os.path.exists(args['<dst>']) and not args['--force']:
        print('dst file already exists. Use -f to overwrite.')
        raise SystemExit

    with open(args['<dst>'], 'wb') as out:

        # Packets for indexing.
        packets, nodes = [], []
        node_seq = 0
        last_root = None
        last_packet = None

        for packet in walk_packets(C10(args['<src>']), args):
            last_packet = packet
            if packet.data_type == 0x03:
                continue

            raw = bytes(packet)
            if len(raw) == packet.packet_length:
                out.write(raw)

            # Just stripping existing indices so move along.
            if args['--strip']:
                continue

            packets.append(packet)

            # Projected index node packet size.
            size = 24 + 4 + 8 + (20 * len(packets))
            if packet.data_type in (0x02, 0x11) or size > 524000:
                offset, raw = gen_node(packets, node_seq)
                node_seq = increment(node_seq)
                nodes.append(offset)
                out.write(raw)
                packets = []

                # Projected root index packet size.
                size = 24 + 4 + (16 * len(nodes)) + 16
                if size > 524000:
                    last_root, raw = gen_root(nodes, last_root, node_seq,
                                              last_packet)
                    out.write(raw)
                    node_seq = increment(node_seq)
                    nodes = []

        # Final indices.
        if packets:
            offset, raw = gen_node(packets)
            nodes.append(offset)
            out.write(raw)
        if nodes:
            offset, raw = gen_root(nodes, last_root, node_seq, last_packet)
            out.write(raw)

    if args['--strip']:
        print('Stripped existing indices.')

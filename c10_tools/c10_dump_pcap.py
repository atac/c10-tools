#!/usr/bin/env python

"""Extract ethernet data from a chapter 10 file and export as a pcap file.

usage: c10-dump-pcap <src> <dst> <channel> [options]

Options:
    -q          Don't display progress bar
    -f --force  Overwrite existing files."""

from time import mktime
import os
import struct
import sys

from docopt import docopt
from dpkt.ethernet import Ethernet
from dpkt.ip import IP
from dpkt.pcap import Writer
from dpkt.udp import UDP

from c10_tools.common import walk_packets, FileProgress, get_time, C10


def main(args=sys.argv[1:]):

    # Get commandline args.
    args = docopt(__doc__, args)
    args['<channel>'] = int(args['<channel>'])

    # Don't overwrite unless explicitly required.
    if os.path.exists(args['<dst>']) and not args['--force']:
        print('dst file already exists. Use -f to overwrite.')
        raise SystemExit

    # Open input and output files.
    with open(args['<dst>'], 'wb') as out, FileProgress(args['<src>']) \
            as progress:

        writer = Writer(out)
        last_time = None

        # Iterate over packets based on args.
        for packet in walk_packets(C10(args['<src>']), args):

            progress.update(packet.packet_length)

            # Track time
            if packet.data_type == 0x11:
                last_time = packet
                continue

            if packet.channel_id != args['<channel>']:
                continue

            for msg in packet:
                data = msg.data

                # Ethernet format 1 (ARINC 664)
                if packet.data_type == 0x69:
                    udp = UDP(
                        sport=msg.src_port,
                        dport=msg.dst_port,
                        data=data)
                    ip = IP(data=udp,
                            len=len(udp),
                            v=4,
                            p=17,
                            src=struct.pack('>L', msg.source_ip),
                            dst=struct.pack('>L', msg.dest_ip)).pack()
                    ethernet = Ethernet(
                        data=ip,
                        len=len(ip),
                        dst=struct.pack('>IH', 50331648, msg.virtual_link),
                        src=bytes()
                    )

                    data = ethernet.pack()

                t = get_time(msg.intra_packet_timestamp, last_time)
                t = mktime(t.timetuple()) + (t.microsecond/1000000.0)
                writer.writepkt(data, t)


if __name__ == '__main__':
    main()

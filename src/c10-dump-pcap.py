#!/usr/bin/env python

"""Extract ethernet data from a chapter 10 file and export as a pcap file.

usage: c10-dump-pcap <src> <dst> <channel> [options]

Options:
    -q          Don't display progress bar
    -f --force  Overwrite existing files."""

from time import mktime
import os

from docopt import docopt
from dpkt.pcap import Writer
from i106 import C10

from common import walk_packets, FileProgress, get_time


if __name__ == '__main__':

    # Get commandline args.
    args = docopt(__doc__)
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
                t = get_time(msg.rtc, last_time)
                t = mktime(t.timetuple()) + (t.microsecond/1000000.0)
                writer.writepkt(msg, t)

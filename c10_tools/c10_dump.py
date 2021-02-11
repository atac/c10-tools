#!/usr/bin/env python

"""usage: c10-dump <file> <channel> [options]

Dump hex (default), or binary data from a channel.

Options:
    -c COUNT, --count COUNT  Number of bytes to show.
    -b BYTEOFFSET, --byteoffset BYTEOFFSET  Offset into message.
    --bin, --binary  Output in raw binary format (useful for exporting video).
    -p, --pcap  Output in PCAP format (ethernet only).
"""

from array import array
import sys

from docopt import docopt

from c10_tools.common import FileProgress, C10, get_time


def main(args=sys.argv[1:]):

    # Get commandline args.
    args = docopt(__doc__, args)
    for arg in ('--count', '--byteoffset', '<channel>'):
        if args.get(arg):
            args[arg] = int(args[arg])

    # Iterate over packets based on args.
    last_time = None
    with FileProgress(args['<file>']) as progress:
        if sys.stdout.isatty():
            progress.close()

        for packet in C10(args['<file>']):
            progress.update(packet.packet_length)

            if packet.data_type == 0x11:
                last_time = packet

            elif packet.channel_id == args['<channel>']:
                for msg in packet:
                    rtc = packet.rtc
                    if hasattr(msg, 'ipts'):
                        rtc = msg.ipts
                    data_bytes = msg.data[args['--byteoffset']:args['--count']]

                    if args['--binary']:
                        if packet.data_type in list(range(0x40, 0x45)):
                            ts = array('H', msg.data)
                            ts.byteswap()
                            sys.stdout.buffer.write(ts.tobytes())
                        else:
                            sys.stdout.buffer.write(msg.data)
                    else:
                        print(get_time(rtc, last_time),
                              ' '.join(
                                  f'{b:02x}'.zfill(2) for b in data_bytes))

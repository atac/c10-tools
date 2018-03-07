#!/usr/bin/env python

"""usage: c10-stat <file> [options]

Options:
    -c CHANNEL..., --channel CHANNEL...  Specify channels to include (csv).
    -e CHANNEL..., --exclude CHANNEL...  Specify channels to ignore (csv).
    -t TYPE, --type TYPE                 The types of data to show (csv, may \
be decimal or hex eg: 0x40).
"""

from __future__ import print_function

from docopt import docopt

from i106 import C10

from common import walk_packets, fmt_number, fmt_size, FileProgress


TYPES = (
    'Computer Generated',
    'PCM',
    'Time',
    'Mil-STD-1553',
    'Analog',
    'Discrete',
    'Message',
    'ARINC 429',
    'Video',
    'Image',
    'UART',
    'IEEE-1394',
    'Parallel',
    'Ethernet',
    'TSPI/CTS Data',
    'Controller Area Network Bus',
)


def main():

    # Get commandline args.
    args = docopt(__doc__)

    channels = {}

    with FileProgress(args['<file>']) as progress:

        # Iterate over selected packets based on args.
        for packet in walk_packets(C10(args['<file>']), args):
            key = (packet.channel_id, packet.data_type)
            if key not in channels:
                channels[key] = {'packets': 0,
                                 'size': 0,
                                 'type': packet.data_type,
                                 'id': packet.channel_id}

            channels[key]['packets'] += 1
            channels[key]['size'] += packet.packet_length

            progress.update(packet.packet_length)

    # Print details for each channel.
    print('Channel ID     Data Type' + 'Packets'.rjust(39), 'Size'.rjust(16))
    print('-' * 80)
    packets, size = 0, 0
    for key, channel in sorted(channels.items()):
        print(('Channel %s' % channel['id']).ljust(15), end='')

        datatype = int(channel['type'] / 8.0)
        type_label = TYPES[datatype]
        subtype = channel['type'] - (datatype * 8)

        print(('%s - %s (format %s)' % (hex(channel['type']),
                                        type_label,
                                        subtype)).ljust(35), end='')
        print(fmt_number(channel['packets']).rjust(13), end='')
        print(fmt_size(channel['size']).rjust(17))
        packets += channel['packets']
        size += channel['size']

    # Print file summary.
    print('-' * 80)
    print('''Summary for %s:
    Channels: %s
    Packets: %s
    Size: %s''' % (
        args['<file>'], len(channels), fmt_number(packets), fmt_size(size)))


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')

#!/usr/bin/env python

"""usage: c10-stat <file> [<file>...] [options]

Options:
    -c CHANNEL..., --channel CHANNEL...  Specify channels to include (csv).
    -e CHANNEL..., --exclude CHANNEL...  Specify channels to ignore (csv).
    -t TYPE, --type TYPE                 The types of data to show (csv, may \
be decimal or hex eg: 0x40).
"""

from contextlib import suppress
import sys

from docopt import docopt

from c10_tools import common


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


def main(args=sys.argv[1:]):

    # Get commandline args.
    args = docopt(__doc__, args)

    last_time = 0

    for filename in args['<file>']:
        start_time, end_time = 0, 0
        channels = {}

        with common.FileProgress(filename) as progress, \
                suppress(KeyboardInterrupt):

            # Iterate over selected packets based on args.
            for packet in common.walk_packets(filename, args):
                if packet.data_type == 0x11:
                    last_time = packet
                    if not start_time:
                        start_time = packet.time
                key = (packet.channel_id, packet.data_type)
                if key not in channels:
                    channels[key] = {'packets': 0,
                                     'size': 0,
                                     'type': packet.data_type,
                                     'id': packet.channel_id}

                channels[key]['packets'] += 1
                channels[key]['size'] += packet.packet_length

                progress.update(packet.packet_length)

        end_time = common.get_time(packet.rtc, last_time)

        # Print details for each channel.
        table = [('Channel ID', 'Data Type', 'Packets', 'Size')]
        packets, size = 0, 0
        for key, channel in sorted(channels.items()):
            datatype = channel['type'] // 8
            subtype = channel['type'] - (datatype * 8)
            table.append((
                f'Channel {channel["id"]:2}',
                f'0x{channel["type"]:02x} - {TYPES[datatype]} (format \
{subtype})',
                common.fmt_number(channel['packets']),
                common.fmt_size(channel['size'])))

            packets += channel['packets']
            size += channel['size']

        print(common.fmt_table(table))

        # Print file summary.
        duration = str(end_time - start_time)
        # TODO: Only show year if format provides it. Requires i106 update.
        start_time = start_time.strftime('%j-%Y %H:%M:%S')
        end_time = end_time.strftime('%j-%Y %H:%M:%S')

        print(f'''Summary for {filename}:
    Channels: {len(channels):>17}     Start time:{start_time:>25}
    Packets: {common.fmt_number(packets):>18}     End time:{end_time:>27}
    Size: {common.fmt_size(size):>21}     Duration:{duration:>27}\n''')


if __name__ == '__main__':
    main()

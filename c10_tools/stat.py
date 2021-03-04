#!/usr/bin/env python

from contextlib import suppress
from urllib.parse import urlparse
import os

from docopt import docopt
from termcolor import colored
import s3fs

from c10_tools.common import C10, FileProgress, fmt_number, fmt_size, fmt_table


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


# Temporary wrapper to allow for c10-stat invocation
def wrapper():
    print(colored('This will be deprecated in favor of c10 stat', 'red'))
    args = docopt('''
Usage:
    c10-stat <file> [<file>...] [options]
''')

    for line in main(args):
        print(line)


def scan_file(filename):
    """Skim the headers of a file and count packets and data size per channel.
    """

    channels, start_time = {}, 0

    # Get file object and size
    # S3 Format: s3://user:pass@host:port/bucket/path.c10
    if filename.startswith('s3://'):
        path = urlparse(filename)
        endpoint = f'http://{path.hostname}:{path.port}'
        fs = s3fs.S3FileSystem(key=path.username,
                               secret=path.password,
                               client_kwargs={
                                   'endpoint_url': endpoint})
        f = fs.open(path.path[1:])
        size = fs.du(path.path[1:])
    else:
        f = open(filename, 'rb')
        size = os.stat(filename).st_size

    # Walk through packets and track counts.
    with FileProgress(total=size) as progress, suppress(KeyboardInterrupt):
        try:
            for packet in C10(f):
                if not start_time and packet.data_type == 0x11:
                    start_time = packet
                key = (packet.channel_id, packet.data_type)
                if key not in channels:
                    channels[key] = {'packets': 1,
                                     'size': packet.packet_length,
                                     'type': packet.data_type,
                                     'id': packet.channel_id}
                else:
                    channels[key]['packets'] += 1
                    channels[key]['size'] += packet.packet_length

                progress.update(packet.packet_length)

        finally:
            f.close()

    return channels, start_time, packet.get_time()


def file_summary(filename, channels, start_time, end_time):
    """Summarize channels and the file as a whole."""

    # Print channel details.
    table = [('Channel ID', 'Data Type', 'Packets', 'Size')]
    packets, size = 0, 0
    for key, channel in sorted(channels.items()):
        datatype = channel['type'] // 8
        subtype = channel['type'] - (datatype * 8)
        table.append((
            f'Channel {channel["id"]:2}',
            f'0x{channel["type"]:02x} - {TYPES[datatype]} (format \
{subtype})',
            fmt_number(channel['packets']),
            fmt_size(channel['size'])))

        packets += channel['packets']
        size += channel['size']

    yield fmt_table(table)

    # Print file summary.
    duration, end_time = 0, 0
    if start_time:
        duration = str(end_time - start_time.time)
        fmt = '%j-%Y %H:%M:%S' if start_time.date_format else '%j %H:%M:%S'
        start_time = start_time.time.strftime(fmt)
        end_time = end_time.strftime(fmt)

    yield f'''Summary for {filename}:
Channels: {len(channels):>17}     Start time:{start_time:>25}
Packets: {fmt_number(packets):>18}     End time:{end_time:>27}
Size: {fmt_size(size):>21}     Duration:{duration:>27}\n'''


def main(args):
    """Inspect one or more Chapter 10 files and get channel info.
    stat <file> [<file>...] [options]
    """

    for filename in args['<file>']:
        try:
            channels, start, end = scan_file(filename)
        except Exception as err:
            print(f'Failed to read file {filename} with \
{err.__class__.__name__}: {err}')
            continue
        yield from file_summary(filename, channels, start, end)


if __name__ == '__main__':
    main()

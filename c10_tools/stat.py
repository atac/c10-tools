
from contextlib import suppress
from urllib.parse import urlparse
import os

from termcolor import colored
import s3fs

from c10_tools.common import C10, FileProgress, fmt_number, fmt_size, \
    fmt_table, walk_packets


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


class Stat:
    def __init__(self, filename, args):
        self.filename = filename
        self.args = args
        self.channels, self.start_time = {}, 0

    def parse(self):
        try:
            self.scan_file()
        except:
            return
        yield from self.file_summary()

    def scan_file(self):
        """Skim the headers of a file and count packets and data size per channel.
        """

        # Get file object and size
        # S3 Format: s3://user:pass@host:port/bucket/path.c10
        if self.filename.startswith('s3://'):
            path = urlparse(self.filename)
            endpoint = f'http://{path.hostname}:{path.port}'
            fs = s3fs.S3FileSystem(key=path.username,
                                   secret=path.password,
                                   client_kwargs={
                                       'endpoint_url': endpoint})
            f = fs.open(path.path[1:])
            size = fs.du(path.path[1:])
        else:
            f = open(self.filename, 'rb')
            size = os.stat(self.filename).st_size

        # Walk through packets and track counts.
        with FileProgress(total=size) as progress, suppress(KeyboardInterrupt):
            try:
                for packet in walk_packets(C10(f), self.args):
                    if not self.start_time and packet.data_type == 0x11:
                        self.start_time = packet
                    key = (packet.channel_id, packet.data_type)
                    if key not in self.channels:
                        self.channels[key] = {'packets': 1,
                                              'size': packet.packet_length,
                                              'type': packet.data_type,
                                              'id': packet.channel_id,
                                              '1553_errors': [0, 0, 0],
                                              '1553_commands': set(),
                                              'events': {}}
                    else:
                        self.channels[key]['packets'] += 1
                        self.channels[key]['size'] += packet.packet_length

                    if self.args['--verbose']:
                        # Track 1553 error counts and command words
                        if packet.data_type == 0x19:
                            for msg in packet:
                                self.channels[key]['1553_commands'].add(
                                    f'{msg.data[0]:0x}'.zfill(2) + f'{msg.data[1]:0x}'.zfill(2))
                                for i, err in enumerate(('le', 'se', 'we')):
                                    err = getattr(msg, err)
                                    self.channels[key]['1553_errors'][i] += err

                        # Record events
                        elif packet.data_type == 0x2:
                            event_list = self.channels[key]['events']
                            for event in packet:
                                if event.number not in event_list:
                                    event_list[event.number] = 1
                                else:
                                    event_list[event.number] += 1

                    progress.update(packet.packet_length)

            except Exception as err:
                print(f'Failed to read file {self.filename} at offset \
{progress.n} with {err.__class__.__name__}: {err}')
                raise

            finally:
                f.close()

        try:
            self.end_time = packet.get_time()
        except UnboundLocalError:
            self.end_time = None

    def file_summary(self):
        """Summarize channels and the file as a whole."""

        # Print channel details.
        table = [('Channel ID', 'Data Type', 'Packets', 'Size')]
        packets, size = 0, 0
        for key, channel in sorted(self.channels.items()):
            datatype = channel['type'] // 8
            subtype = channel['type'] - (datatype * 8)
            table.append((
                f'Channel {channel["id"]:2}',
                f'0x{channel["type"]:02x} - {TYPES[datatype]} (format \
{subtype})',
                fmt_number(channel['packets']),
                fmt_size(channel['size'])))

            if self.args['--verbose']:
                if channel['type'] == 0x19:
                    table.append((f'  Command words ({len(channel["1553_commands"])}):',))
                    for command in sorted(channel['1553_commands']):
                        table.append((f'    {command}',))
                    total = sum(channel['1553_errors'])
                    if total:
                        error_str = '  Err: ' + f'{total:>11,}'
                        for i, err in enumerate(('Length', 'Sync', 'Word')):
                            count = channel['1553_errors'][i]
                            error_str += f'  {err}: {count:>9,}'.ljust(14)
                        table.append((colored(error_str + ' ', 'red'),))
                elif channel['type'] == 0x2:
                    table.append(('  Events:',))
                    for event, count in sorted(channel['events'].items()):
                        table.append((f'{event:>8}: {count:>10}',))

            packets += channel['packets']
            size += channel['size']

        yield fmt_table(table)

        # Print file summary.
        duration = 0
        start_time, end_time = 0, 0
        if self.start_time:
            duration = str(self.end_time - self.start_time.time)
            fmt = '%j %H:%M:%S'
            if self.start_time.date_format:
                fmt = '%j-%Y %H:%M:%S'
            start_time = self.start_time.time.strftime(fmt)
            end_time = self.end_time.strftime(fmt)

        yield f'''Summary for {self.filename}:
    Channels: {len(self.channels):>17}     Start time:{start_time:>25}
    Packets: {fmt_number(packets):>18}     End time:{end_time:>27}
    Size: {fmt_size(size):>21}     Duration:{duration:>27}\n'''


def main(args):
    """Inspect one or more Chapter 10 files and get channel info.
    stat <file> [<file>...] [options]
    -c CHANNEL..., --channel CHANNEL...  Specify channels to include (comma \
separated).
    -e CHANNEL..., --exclude CHANNEL...  Specify channels to ignore (comma \
separated).
    -t TYPE, --type TYPE  The types of data to copy (comma separated, may be \
decimal or hex eg: 0x40)
    """

    for filename in args['<file>']:
        stats = Stat(filename, args)
        yield from stats.parse()

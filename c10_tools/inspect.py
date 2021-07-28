
from collections import OrderedDict
import asyncio
import csv
import os
import sys

from chapter10 import C10
from termcolor import colored

from .common import fmt_number, FileProgress, walk_packets


class Inspect:
    KEYS = {
        'Channel': 'channel_id',
        'Type': 'data_type',
        'Sequence': 'sequence_number',
        'Size': 'packet_length',
    }

    # TODO: selectable columns
    # Pairs of (name, width)
    COLUMNS = OrderedDict((
        ('Channel', 7),
        ('Type', 4),
        ('Sequence', 8),
        ('Size', 7),
        ('Time', 27),
        ('Valid', 5),
        ('Offset', 15),
    ))

    def __init__(self, args):
        self.args = args
        self.cols = self.COLUMNS

        # Use CSV if stdout is redirected
        self.writer = None
        if os.fstat(0) != os.fstat(1):
            self.writer = csv.writer(sys.stdout, lineterminator='')

    def get_size(self):
        """Get total byte size for all files."""

        return sum(os.stat(f).st_size for f in self.args['<file>'])

    def write_header(self):
        """Write out header row for CSV or ASCII."""

        if self.writer:
            self.writer.writerow(self.cols.keys())
            return ''

        else:
            s = ' | '.join([f'{key:<{width}}'
                            for key, width in self.cols.items()])
            line = '-' * (len(s) + 4)
            return f'{line}\n| {s} |\n{line}'

    def write_row(self, packet, offset):
        """Pull values from a packet and write output row."""

        row = []
        for col, width in self.cols.items():
            if col == 'Time':
                if packet.data_type == 1:
                    val = 'N/A'
                else:
                    if packet.data_type == 0x11:
                        self.date_format = packet.date_format

                    # Julian day or month/year
                    fmt = '%j %H:%M:%S.%f'
                    if self.date_format:
                        fmt = '%Y-%m-%d %H:%M:%S.%f'

                    val = packet.get_time().strftime(fmt)
            elif col == 'Valid':
                val = packet.validate(True) and 'Yes' or 'No'
            elif col == 'Offset':
                val = offset
            elif col in self.KEYS:
                val = getattr(packet, self.KEYS[col])

            if not self.writer and isinstance(val, (float, int)):
                val = fmt_number(val).rjust(width)

            row.append(val)

        s = ''
        if self.writer:
            self.writer.writerow(row)

        else:
            widths = list(self.cols.values())
            s = '|'
            for i, col in enumerate(row):
                s += f' {col:<{widths[i]}} |'

        return s

    async def get_packet(self, c10):
        """Read and return the next packet from a file or raise
        StopAsyncIteration.
        """

        try:
            packet = next(c10)
            assert packet.packet_length == len(bytes(packet)), \
                'Packet length incorrect'
        except StopIteration:
            raise StopAsyncIteration
        return packet

    def find_sync(self, f):
        """Seek forward in a file to the next sync pattern (eb25)."""

        while True:
            offset = f.tell()
            buffer = f.read(100000)
            if not buffer:
                raise EOFError
            if b'\x25\xeb' in buffer:
                f.seek(offset + buffer.find(b'\x25\xeb'))
                return f.tell()

    def parse_file(self, f, progress):
        """Walk a file and read header information."""

        offset = 0
        c10 = walk_packets(C10(f), self.args, include_time=False)
        while True:

            # Try to read a packet.
            try:
                packet = asyncio.run(
                    asyncio.wait_for(self.get_packet(c10), timeout=.1))
                yield self.write_row(packet, offset)
                progress.update(packet.packet_length)
                offset += packet.packet_length

            # Report error and retry at the next sync pattern.
            except Exception as err:

                # Exit if we've read the whole file.
                if offset >= os.stat(f.name).st_size:
                    break

                if not isinstance(err, StopAsyncIteration):
                    msg = f'{err} at {fmt_number(offset)}'
                    if self.writer is None:
                        yield colored(msg, 'red')
                    else:
                        yield f'"{msg}"'

                try:
                    f.seek(offset + 1, 1)
                    sync = self.find_sync(f)
                except EOFError:
                    break
                progress.update(sync - offset)
                offset = sync

    def main(self):
        with FileProgress(total=self.get_size()) as progress:
            if self.args['--quiet'] or not self.writer:
                progress.close()

            header = self.write_header()
            yield header

            for f in self.args['<file>']:
                with open(f, 'rb') as f:
                    yield from self.parse_file(f, progress)

            # Closing line if we're in ASCII mode.
            if header:
                yield header.split('\n', 1)[0]


def main(args):
    """Report on packets found in a file.
    inspect <file>... [options]
    -c CHANNEL..., --channel CHANNEL...  Specify channels to include (comma \
separated).
    -e CHANNEL..., --exclude CHANNEL...  Specify channels to ignore (comma \
separated).
    -t TYPE, --type TYPE  The types of data to copy (comma separated, may be \
decimal or hex eg: 0x40)
    """

    yield from Inspect(args).main()
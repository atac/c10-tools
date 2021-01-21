
from datetime import timedelta, datetime
import os

from tqdm import tqdm

# Allow for explicit parser selection, or else use pychapter10 by default.
from chapter10 import C10
if os.environ.get('LIBRARY', 'c10') == 'i106':
    try:
        from i106 import C10
    except ImportError:
        print('Could not import libirig106-python, reverting to pychapter10')


# Format a number nicely with commas for thousands, etc.
fmt_number = '{0:,}'.format


def find_c10(paths):
    """Take a list of paths and yield paths to Chapter 10 files found at
    those locations or subdirectories. Any files in the original list are
    returned as-is.
    """

    for path in paths:
        path = os.path.abspath(path)
        if os.path.isdir(path):
            for dirname, dirnames, filenames in os.walk(path):
                for f in filenames:
                    if os.path.splitext(f)[1].lower() in ('.c10', '.ch10'):
                        yield os.path.join(dirname, f)
        else:
            yield path


def fmt_table(table):
    """Print tabular data to stdout. Numeric fields justified right, others
    left.
    """

    # Make a list of columns (instead of a list of rows) and find max widths.
    col_widths = [max(len(x) for x in col) for col in zip(*table)]

    # Width is the sum of the column widths + ~3 padding characters per column.
    width = sum(col_widths) + (len(table[0]) * 3) + 1

    # Header row
    s = ('-' * width) + '\n|'
    for i, x in enumerate(table[0]):
        s += ' ' + x.ljust(col_widths[i]) + ' |'
    s += '\n{}\n'.format('-' * width)

    # Data rows
    size_suffix = (' kb', ' mb', ' gb', '  b')
    for row in table[1:]:
        s += '|'
        for i, x in enumerate(row):
            if x.replace(',', '').isdigit() or x[-3:] in size_suffix:
                s += ' {} |'.format(x.rjust(col_widths[i]))
            else:
                s += ' {} |'.format(x.ljust(col_widths[i]))
        s += '\n'

    return s + ('-' * width)


def get_time(rtc, time_packet):
    """Get a datetime object based on last time packet and an RTC value."""

    # TODO: this is here because the event sample file has no time
    if time_packet is None:
        return datetime.now()

    rtc -= time_packet.rtc
    return time_packet.time + timedelta(seconds=rtc / 10_000_000)


def fmt_size(size):
    """Convert byte size to a more readable format (mb, etc.)."""

    unit, units = ' b', ['gb', 'mb', 'kb']
    while size > 1024 and units:
        size /= 1024.0
        unit = units.pop()
    return '{} {}'.format(round(size, 2), unit)


def walk_packets(c10, args={}):
    """Walk a chapter 10 file based on sys.argv (type, channel, etc.)."""

    # Apply defaults.
    args['--type'] = args.get('--type') or ''
    args['--channel'] = args.get('--channel') or ''
    args['--exclude'] = args.get('--exclude') or ''

    # Parse types (if given) into ints.
    types = [t.strip() for t in args['--type'].split(',') if t.strip()]
    types = [int(t, 16) if t.startswith('0x') else int(t) for t in types]

    # Parse channel selection.
    channels = [c.strip() for c in args['--channel'].split(',') if c.strip()]
    exclude = [e.strip() for e in args['--exclude'].split(',') if e.strip()]

    # Filter packets (except the TMATS packet that should be at 0).
    for i, packet in enumerate(c10):
        if i > 0:
            channel = str(packet.channel_id)
            if channels and channel not in channels:
                continue
            elif channel in exclude:
                continue
            elif types and packet.data_type not in types:
                continue

        yield packet


class FileProgress(tqdm):
    """Extend tqdm to show progress reading over a file based on f.tell()."""

    def __init__(self, filename=None, total=None, **kwargs):
        if total is None:
            total = os.stat(filename).st_size
        tqdm_kwargs = dict(
            dynamic_ncols=True,
            total=total,
            leave=False,
            unit='bytes',
            unit_scale=True)
        tqdm_kwargs.update(kwargs)
        tqdm.__init__(self, **tqdm_kwargs)
        self.last_tell = 0

    def update_from_tell(self, tell):
        self.update(tell - self.last_tell)
        self.last_tell = tell

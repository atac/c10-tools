
import functools
import locale
import os


from tqdm import tqdm


locale.setlocale(locale.LC_ALL, 'en_US')


# Format a number nicely with commas for thousands, etc.
fmt_number = functools.partial(locale.format, '%d', grouping=True)


def fmt_size(size):
    """Convert byte size to a more readable format (mb, etc.)."""

    units = ['gb', 'mb', 'kb']
    unit = 'b'
    while size > 1024 and units:
        size /= 1024.0
        unit = units.pop()

    return '%s %s' % (round(size, 2), unit)


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

    for i, packet in enumerate(c10):
        if i > 0:
            if channels and str(packet.channel_id) not in channels:
                continue
            elif str(packet.channel_id) in exclude:
                continue
            elif types and packet.data_type not in types:
                continue

        yield packet


class FileProgress(tqdm):
    """Extend tqdm to show progress reading over a file based on f.tell()."""

    def __init__(self, filename):
        tqdm.__init__(self, dynamic_ncols=True,
                      total=os.stat(filename).st_size,
                      unit='bytes',
                      unit_scale=True)
        self.last_tell = 0

    def update_from_tell(self, tell):
        self.update(tell - self.last_tell)
        self.last_tell = tell

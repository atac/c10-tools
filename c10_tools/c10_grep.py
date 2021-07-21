
"""usage: c10-grep <value> <path>... [options]

Find occurrences of a given value in Chapter 10 data.
Can search multiple files or directories simultaneously.
Use "*" for value to see all data at that offset.

Options:
    -c CHANNEL, --channel CHANNEL  Channel ID
    --cmd CMDWORD                  1553 Command word
    -o OFFSET, --offset OFFSET     Byte offset within message [default: 0]
    -m MASK, --mask=MASK           Value mask
"""

import os
import sys
import struct

from docopt import docopt
from tqdm import tqdm

from c10_tools.common import get_time, FileProgress, find_c10, C10


def word(b):
    """Combine two bytes into a 16-bit word."""

    return struct.unpack('=H', struct.pack('=BB', b[0], b[1]))[0]


def search(path, args, i=None):
    """Search file "path" based on parameters from "args"."""

    print(path)

    for packet in C10(path):

        # Match channel
        if args.get('--channel') and args.get('--channel') != packet.channel_id:
            continue

        # Iterate over messages
        for msg in packet:
            # 1553
            if packet.data_type == 0x19:

                # Match command word
                cmd = word(msg.data[:2])
                if args.get('--cmd') and args.get('--cmd') != cmd:
                    continue

                offset = args.get('--offset')
                try:
                    value = word(msg.data[offset:offset+2])
                except IndexError:
                    continue

            else:
                value = msg.data[args.get('--offset')]

            if args.get('--mask') is not None:
                value &= args.get('--mask')

            if args.get('<value>') == '*':
                print(hex(value))
            elif value == args.get('<value>'):
                print(f'    {packet.get_time()}\n')


def main(args=sys.argv[1:]):

    args = docopt(__doc__, args)

    # Validate int/hex inputs.
    for key in ('--channel', '--offset', '--cmd', '<value>', '--mask'):
        value = args.get(key)
        if not value:
            continue
        if key == '<value>' and value == '*':
            continue
        try:
            if args[key].lower().startswith('0x'):
                args[key] = int(args[key], 16)
            else:
                args[key] = int(args[key])
        except ValueError:
            print('Invalid value "%s" for %s' % (args[key], key))
            raise SystemExit

    # Describe the search parameters.
    value_repr = args.get('<value>')
    if isinstance(value_repr, int):
        value_repr = hex(value_repr)
    print('Searching for %s' % value_repr, end='')
    if args.get('--channel'):
        print(' in channel #%s' % args.get('--channel'), end='')
    if args.get('--cmd'):
        print(' with command word %s' % hex(args.get('--cmd')), end='')
    if args.get('--offset'):
        print(' at word %s' % args.get('--offset'), end='')
    if args.get('--mask'):
        print(' with mask %s' % hex(args.get('--mask')), end='')

    files = list(find_c10(args.get('<path>')))

    print(' in %s files...' % len(files))
    files = tqdm(
        files,
        desc='Overall',
        unit='files',
        dynamic_ncols=True,
        leave=False)
    if os.fstat(0) == os.fstat(1):
        files.close()
    for f in files:
        search(f, args)
    print('\nfinished')

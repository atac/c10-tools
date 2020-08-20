#!/usr/bin/env python

"""usage: c10-grep <value> <path>... [options]

Search Chapter 10 files/directories for "<value>" based on user input.
Use "*" for value to see all data at that address.

Options:
    -c CHANNEL, --channel CHANNEL  Channel ID
    --cmd CMDWORD                  1553 Command word
    -w WORD, --word-offset WORD    Word offset within message [default: 0]
    -m MASK, --mask=MASK           Value mask
    -o OUTFILE, --output OUTFILE   Print results to file
    -f, --force                    Overwrite existing output file
    -x                             Utilize multiprocessing via dask (works, \
but progress reporting is a little exciting)
"""

from functools import partial
import os
import struct
import sys

from dask.delayed import delayed
from docopt import docopt
from tqdm import tqdm
import dask.bag as db

from c10_tools.common import get_time, FileProgress, find_c10, C10


def swap_word(word):
    return struct.unpack('<H', struct.pack('>H', word))[0]


def search(path, args, i=None):
    """Search file "path" based on parameters from "args"."""

    outfile = sys.stdout
    if args.get('--output'):
        outfile = open(args.get('--output'), 'a')

    outfile.write(path + '\n')

    last_time = None
    with FileProgress(
            filename=path,
            desc='    ' + os.path.basename(path),
            ascii=False,
            position=i) as progress:

        if outfile == sys.stdout:
            progress.close()

        for packet in C10(path):

            progress.update(packet.packet_length)

            if packet.data_type == 0x11:
                last_time = packet

            # Match channel
            if (args.get('--channel') or packet.channel_id) != \
                    packet.channel_id:
                continue

            # Iterate over messages if applicable
            for msg in packet:
                if hasattr(msg, 'data'):
                    msg = msg.data
                if packet.data_type == 0x19:
                    cmd = msg[0]

                    # Match command word
                    if args.get('--cmd') and args.get('--cmd') != cmd:
                        continue

                    value = msg[args.get('--word-offset')]

                    if args.get('--mask') is not None:
                        value &= args.get('--mask')

                    if args.get('<value>') == '*':
                        print(hex(value))
                    elif value == args.get('<value>'):
                        outfile.write((' ' * 4) + str(get_time(
                            msg.rtc, last_time)) + '\n')

    if outfile != sys.stdout:
        outfile.close()


def main(args=sys.argv[1:]):

    args = docopt(__doc__, args)

    # Validate int/hex inputs.
    for opt in ('--channel', '--word-offset', '--cmd', '<value>', '--mask'):
        if args.get(opt):
            if opt == '<value>' and args[opt] == '*':
                continue
            try:
                if args[opt].lower().startswith('0x'):
                    args[opt] = int(args[opt], 16)
                else:
                    args[opt] = int(args[opt])
            except ValueError:
                print('Invalid value "%s" for %s' % (args[opt], opt))
                raise SystemExit

    if args.get('--output') and os.path.exists(args.get('--output')):
        if args.get('--force'):
            with open(args.get('--output'), 'w') as f:
                f.write('')
        else:
            print('Output file exists, use -f to overwrite.')
            raise SystemExit

    # Describe the search parameters.
    value_repr = args.get('<value>')
    if isinstance(value_repr, int):
        value_repr = hex(value_repr)
    print('Searching for %s' % value_repr, end='')
    if args.get('--channel'):
        print('in channel #%s' % args.get('--channel'), end='')
    if args.get('--cmd'):
        print('with command word %s' % hex(args.get('--cmd')), end='')
    if args.get('--word-offset'):
        print('at word %s' % args.get('--word-offset'), end='')
    if args.get('--mask'):
        print('with mask %s' % hex(args.get('--mask')), end='')

    files = list(find_c10(args.get('<path>')))

    print(' in %s files...' % len(files))
    task = partial(search, args=args)
    if args.get('-x'):
        bag = db.from_delayed([
            delayed(task)(f, i=i) for i, f in enumerate(files)])
        bag.compute()
    else:
        files = tqdm(
            files,
            desc='Overall',
            unit='files',
            dynamic_ncols=True,
            leave=False)
        if not args.get('--output'):
            files.close()
        for f in files:
            task(f)
    print('\nfinished')


if __name__ == '__main__':
    main()

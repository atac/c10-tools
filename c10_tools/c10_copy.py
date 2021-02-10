#!/usr/bin/env python

import os
import sys

from termcolor import colored
from docopt import docopt

from c10_tools.common import walk_packets, FileProgress, C10


def wrapper(argv=sys.argv[1:]):
    print(colored('This will be deprecated in favor of c10 copy', 'red'))
    args = docopt('''usage: c10_copy <src> <dst> [options]

Options:
    -c CHANNEL..., --channel CHANNEL...  Specify channels to include (comma \
separated).
    -e CHANNEL..., --exclude CHANNEL...  Specify channels to ignore (comma \
separated).
    -t TYPE, --type TYPE                 The types of data to copy (comma \
separated, may be decimal or hex eg: 0x40)
    -f --force                           Overwrite existing files.''', argv)

    return main(args)


def main(args):
    """Copy a Chapter 10 file. Can be filtered on channel ID or data type.
    copy <src> <dst> [options]
    -c CHANNEL..., --channel CHANNEL...  Specify channels to include (comma \
separated).
    -e CHANNEL..., --exclude CHANNEL...  Specify channels to ignore (comma \
separated).
    -t TYPE, --type TYPE  The types of data to copy (comma separated, may be \
decimal or hex eg: 0x40)
    -f --force  Overwrite existing files.
    """

    # Don't overwrite unless explicitly required.
    if os.path.exists(args['<dst>']) and not args['--force']:
        print('dst file already exists. Use -f to overwrite.')
        raise SystemExit

    # Open input and output files.
    with open(args['<dst>'], 'wb') as out, FileProgress(args['<src>']) \
            as progress:

        src = C10(args['<src>'])

        # Iterate over packets based on args.
        for packet in walk_packets(src, args):

            progress.update(packet.packet_length)

            # Copy packet to new file.
            if packet.data_type:
                out.write(bytes(packet))

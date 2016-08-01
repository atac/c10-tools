#!/usr/bin/env python

"""usage: c10-copy <src> <dst> [options]

Options:
    -c CHANNEL..., --channel CHANNEL...  Specify channels to include (csv).
    -e CHANNEL..., --exclude CHANNEL...  Specify channels to ignore (csv).
    -t TYPE, --type TYPE                 The types of data to copy (csv, may\
 be decimal or hex eg: 0x40)
    -f --force                           Overwrite existing files."""

import os

from chapter10 import C10
from docopt import docopt

from walk import walk_packets


if __name__ == '__main__':

    # Get commandline args.
    args = docopt(__doc__)

    # Don't overwrite unless explicitly required.
    if os.path.exists(args['<dst>']) and not args['--force']:
        print('dst file already exists. Use -f to overwrite.')
        raise SystemExit

    # Open input and output files.
    with open(args['<dst>'], 'wb') as out:
        src = C10(args['<src>'])

        # Iterate over packets based on args.
        for packet in walk_packets(src, args):

            # Copy packet to new file.
            raw = bytes(packet)
            if len(raw) == packet.packet_length:
                out.write(raw)

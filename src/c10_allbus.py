#!/usr/bin/env python

"""usage: c10-allbus <src> <dst> [-b] [options]

Switch 1553 format 1 messages to indicate the same bus (A or B).

Options:
    -b           Use the B bus instead of A (default).
    -f, --force  Overwrite existing dst file if present.
"""

import os
import sys

from docopt import docopt
try:
    from i106 import C10
except ModuleNotFoundError:
    from chapter10 import C10

from .common import FileProgress


def main(args=[]):
    args = docopt(__doc__, args)

    if os.path.exists(args['<dst>']) and not args['--force']:
        print('Destination file exists. Use --force to overwrite it.')
        raise SystemExit

    with open(args['<dst>'], 'wb') as out, \
            FileProgress(args['<src>']) as progress:
        for packet in C10(args['<src>']):

            raw = bytes(packet)
            progress.update(len(raw))

            # Write non-1553 out as-is.
            if packet.data_type != 0x19:
                out.write(raw)
                continue

            # Write out packet header secondary if applicable) and CSDW.
            offset = 28
            if packet.flags & (1 << 7):
                offset += 12
            out.write(raw[:offset])

            # Walk through messages and update bus ID as needed.
            for msg in packet:
                msg.bus = int(args['-b'])
                packed = bytes(msg)
                out.write(packed)
                offset += len(packed)

            # Write filler.
            for i in range(packet.packet_length - offset):
                out.write(b'0')


if __name__ == '__main__':
    main(sys.argv)

#!/usr/bin/env python

import os

from c10_tools.common import FileProgress, C10


def main(args):
    """Switch 1553 format 1 messages to indicate the same bus (a or b).
    allbus <src> <dst> [-b] [options]
    -b  use the b bus instead of a (default).
    -f, --force  overwrite existing dst file if present.
    """

    if os.path.exists(args['<dst>']) and not args['--force']:
        print('Destination file exists. Use --force to overwrite it.')
        raise SystemExit

    with open(args['<dst>'], 'wb') as out, \
            FileProgress(args['<src>']) as progress:
        for packet in C10(args['<src>']):
            progress.update(packet.packet_length)

            if packet.data_type == 0x19:
                for msg in packet:
                    msg.bus = int(args['-b'])

            out.write(bytes(packet))


if __name__ == '__main__':
    main()

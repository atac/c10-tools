#!/usr/bin/env python

import os

from chapter10 import C10
from chapter10.datatypes import MS1553
from docopt import docopt
from tqdm import tqdm


def main(args):
    errcount = 0
    file_size = os.stat(args['<file>']).st_size
    with tqdm(total=file_size, dynamic_ncols=True,
              unit='bytes', unit_scale=True, leave=True) as progress:
        if args['-q']:
            progress.close()
        for packet in C10(args['<file>']):
            if isinstance(packet.body, MS1553) and packet.body.format == 1:
                for msg in packet:
                    errcount += sum([msg.me, msg.fe, msg.le, msg.se, msg.we])
            if not args['-q']:
                progress.update(packet.packet_length)

    print('Total errors: %s' % errcount)


if __name__ == "__main__":
    args = docopt('''Counts error flags in 1553 packets
usage: c10-errcount <file> [-q]''')
    main(args)

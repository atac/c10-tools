#!/usr/bin/env python

from chapter10 import C10
from chapter10.datatypes import MS1553
from docopt import docopt


def main(args):
    errcount = 0
    for packet in C10(args['<file>']):
        if isinstance(packet.body, MS1553) and packet.body.format == 1:
            for msg in packet:
                errcount += sum([msg.me, msg.fe, msg.le, msg.se, msg.we])

    print('Total errors: %s' % errcount)


if __name__ == "__main__":
    args = docopt('''Counts error flags in 1553 packets
usage: c10-errcount <file> [options]''')
    main(args)

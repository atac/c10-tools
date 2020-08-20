#!/usr/bin/env python

'''usage: c10-events <input_file>'''

import sys

from docopt import docopt

from c10_tools.common import C10, get_time


def main(args=sys.argv[1:]):
    args = docopt(__doc__, args)

    last_time = None
    for packet in C10(args['<input_file>']):
        if packet.data_type == 0x11:
            last_time = packet
            continue

        if packet.data_type == 0x2:
            print('Recording Event packet at {}'.format(get_time(
                packet.rtc, last_time)))
            for i, entry in enumerate(packet):
                print(entry.__dict__)
                t = get_time(entry.ipts, last_time)
                print(f'''    {i + 1} of {len(packet)} at {t}
    Occurrence: {entry.occurrence}
    Count: {entry.count}
    Number: {entry.number})''')


if __name__ == '__main__':
    main()

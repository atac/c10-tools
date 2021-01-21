#!/usr/bin/env python

"""usage: c10_headers <file>... [options]"""

import sys

from docopt import docopt

from c10_tools.common import walk_packets, FileProgress, C10


def main(args=sys.argv[1:]):

    # Get commandline args.
    args = docopt(__doc__, args)

    keys = ('channel_id',
            'packet_length',
            'data_length',
            'header_version',
            'sequence_number',
            'secondary_header',
            'ipts_source',
            'rtc_sync_error',
            'data_overflow_error',
            'secondary_format',
            'data_checksum',
            'data_type',
            'rtc',
            'header_checksum')

    for f in args['<file>']:
        for packet in C10(f):
            for k in keys:
                print(k.replace('_', ' ').title(), getattr(packet, k))
            print()


if __name__ == '__main__':
    main()

#!/usr/bin/env python

"""usage: c10-dmp1553 <file> <word> [options]

Print a hex dump of word "<word>" for any 1553 messages found.

Options:
    -w COUNT, --word-count COUNT  Number of words to print out [default: 1].
"""

import sys

from docopt import docopt

from c10_tools.common import C10


def main(args=sys.argv[1:]):

    # Get commandline args.
    args = docopt(__doc__, args)
    word = int(args.get('<word>'))
    size = int(args.get('--word-count'))

    # Iterate over packets based on args.
    for packet in C10(args['<file>']):

        if packet.data_type == 25:
            for msg in packet:
                s = ''
                msg = getattr(msg, 'data', msg)
                for w in msg[word:word + size]:
                    s += f'{w:02x}'.zfill(4) + ' '
                if s:
                    print(s)


if __name__ == '__main__':
    main()

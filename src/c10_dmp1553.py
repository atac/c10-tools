#!/usr/bin/env python

"""usage: c10-dmp1553 <file> <word> [options]

Print a hex dump of word "<word>" for any 1553 messages found.

Options:
    -w COUNT, --word-count COUNT  Number of words to print out [default: 1].
"""

from docopt import docopt

from common import C10


if __name__ == '__main__':

    # Get commandline args.
    args = docopt(__doc__)
    word = int(args.get('<word>'))
    size = int(args.get('--word-count'))

    # Iterate over packets based on args.
    for packet in C10(args['<file>']):

        if packet.data_type == 25:
            for msg in packet:
                s = ''
                for w in msg[word:word + size]:
                    s += f'{w:02x}'.zfill(4) + ' '
                if s:
                    print(s)

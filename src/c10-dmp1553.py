#!/usr/bin/env python

"""usage: i106dmp1553 <file> <word> [options]

Print a hex dump of word "<word>" for any 1553 messages found.

Options:
    -w COUNT, --word-count COUNT  Number of words to print out [default: 1].
"""

from __future__ import print_function

from i106 import C10
from docopt import docopt


if __name__ == '__main__':

    # Get commandline args.
    args = docopt(__doc__)

    word = int(args.get('<word>'))
    size = int(args.get('--word-count'))

    # Iterate over packets based on args.
    for packet in C10(args['<file>']):

        if packet.data_type == 25:
            for msg in packet:
                for w in msg[word:word + size]:
                    print(hex(w)[2:].zfill(4), end=' ')
                print()

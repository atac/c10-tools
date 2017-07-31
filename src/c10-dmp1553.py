#!/usr/bin/env python

"""usage: c10-dmp1553 <file> <word> [options]

Print a hex dump of word "<word>" for any 1553 messages found.

Options:
    -w COUNT, --word-count COUNT  Number of words to print out [default: 1].
"""

from array import array
import struct

from chapter10 import C10
from chapter10.datatypes import MS1553
from docopt import docopt


if __name__ == '__main__':

    # Get commandline args.
    args = docopt(__doc__)

    word = int(args.get('<word>')) * 2
    size = int(args.get('--word-count')) * 2

    # Iterate over packets based on args.
    for packet in C10(args['<file>']):

        if isinstance(packet.body, MS1553):
            for msg in packet.body:
                try:
                    words = array('H', msg.data[word:word + size])
                    for w in words:
                        print hex(w)[2:].zfill(4),
                    print
                except struct.error:
                    continue

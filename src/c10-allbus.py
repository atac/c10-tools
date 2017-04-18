#!/usr/bin/env python

"""usage: c10-allbus <src> <dst> [-b <bus>] [options]

Switch 1553 messages to indicate the same bus (A or B).

Options:
    -b <bus>, --bus <bus>  Indicate which bus to indicate [default: a].
    -f, --force            Overwrite existing dst file if present.
"""

from docopt import docopt
from chapter10 import C10


if __name__ == '__main__':
    args = docopt(__doc__)

    with open(args['<dst>'], 'wb') as out:
        for packet in C10(args['<src>']):

            raw = bytes(packet)

            # Write non-1553 out as-is.
            if packet.data_type != 0x19:
                out.write(raw)

            else:
                # Write out packet header secondary if applicable) and CSDW.
                out.write(raw[:24])
                if packet.secondary_header:
                    out.write(raw[24:36])

                # Walk through messages and update bus ID as needed.
                for msg in packet.body:
                    print msg.bus_id

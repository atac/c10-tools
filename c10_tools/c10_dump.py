#!/usr/bin/env python

"""usage: c10-dump <file> [options]

Options:
    -o OUT, --output OUT                 The directory to place files \
[default: .].
    -c CHANNEL..., --channel CHANNEL...  Specify channels to include(csv).
    -e CHANNEL..., --exclude CHANNEL...  Specify channels to ignore (csv).
    -t TYPE, --type TYPE                 The types of data to export (csv, may\
 be decimal or hex eg: 0x40)
    -f, --force                          Overwrite existing files."""

from array import array
import os
import sys

from docopt import docopt

from c10_tools.common import walk_packets, FileProgress


def main(args=sys.argv[1:]):

    # Get commandline args.
    args = docopt(__doc__, args)

    # Ensure OUT exists.
    if not os.path.exists(args['--output']):
        os.makedirs(args['--output'])

    out = {}

    # Iterate over packets based on args.
    with FileProgress(args['<file>']) as progress:
        for packet in walk_packets(args['<file>'], args):

            progress.update(packet.packet_length)

            # Get filename for this channel based on data type.
            filename = os.path.join(args['--output'], str(packet.channel_id))
            if packet.data_type == 0x1:
                filename += packet.format == 0 and '.tmats' or '.xml'
            elif packet.data_type // 8 == 8:
                filename += '.mpg'

            # Ensure a file is open (and will close) for a given channel.
            if filename not in out:

                # Don't overwrite unless explicitly required.
                if os.path.exists(filename) and not args['--force']:
                    print('%s already exists. Use -f to overwrite.' % filename)
                    break

                out[filename] = open(filename, 'wb')

            # Only write TMATS once.
            elif packet.data_type == 0x1:
                continue

            # Handle special case for video data.
            if packet.data_type // 8 == 8:
                for ts in packet.body:
                    ts = array('H', ts.data)
                    ts.byteswap()
                    ts.tofile(out[filename])
            else:
                header_size = 36 if packet.secondary_header else 24
                data = bytes(packet)[
                    header_size:packet.data_length + header_size]

                # Write out raw packet body.
                out[filename].write(data)


if __name__ == '__main__':
    main()

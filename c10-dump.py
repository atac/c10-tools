#!/usr/bin/env python

"""
  dump.py - Export channel data based on channel ID or data type.

 Copyright (c) 2015 Micah Ferrill

 All rights reserved.

 Redistribution and use in source and binary forms, with or without
 modification, are permitted provided that the following conditions are
 met:

   * Redistributions of source code must retain the above copyright
     notice, this list of conditions and the following disclaimer.

   * Redistributions in binary form must reproduce the above copyright
     notice, this list of conditions and the following disclaimer in the
     documentation and/or other materials provided with the distribution.

   * Neither the name Irig106.org nor the names of its contributors may
     be used to endorse or promote products derived from this software
     without specific prior written permission.

 This software is provided by the copyright holders and contributors
 "as is" and any express or implied warranties, including, but not
 limited to, the implied warranties of merchantability and fitness for
 a particular purpose are disclaimed. In no event shall the copyright
 owner or contributors be liable for any direct, indirect, incidental,
 special, exemplary, or consequential damages (including, but not
 limited to, procurement of substitute goods or services; loss of use,
 data, or profits; or business interruption) however caused and on any
 theory of liability, whether in contract, strict liability, or tort
 (including negligence or otherwise) arising in any way out of the use
 of this software, even if advised of the possibility of such damage.
"""

__doc__ = """usage: dump.py <file> [options]

Options:
    -o OUT, --output OUT                 The directory to place files \
[default: .].
    -c CHANNEL..., --channel CHANNEL...  Specify channels to include(csv).
    -e CHANNEL..., --exclude CHANNEL...  Specify channels to ignore (csv).
    -t TYPE, --type TYPE                 The types of data to export (csv, may\
 be decimal or hex eg: 0x40)
    -f, --force                          Overwrite existing files."""

import atexit
import os

from chapter10 import C10, datatypes
from docopt import docopt

from walk import walk_packets


if __name__ == '__main__':

    # Get commandline args.
    args = docopt(__doc__)

    # Ensure OUT exists.
    if not os.path.exists(args['--output']):
        os.makedirs(args['--output'])

    out = {}

    # Iterate over packets based on args.
    for packet in walk_packets(C10(args['<file>']), args):

        # Get filename for this channel based on data type.
        filename = os.path.join(args['--output'], str(packet.channel_id))
        t, f = datatypes.format(packet.data_type)
        if t == 0 and f == 1:
            filename += packet.body.frmt == 0 and '.tmats' or '.xml'
        elif t == 8:
            filename += '.mpg'

        # Ensure a file is open (and will close) for a given channel.
        if filename not in out:

            # Don't overwrite unless explicitly required.
            if os.path.exists(filename) and not args['--force']:
                print('%s already exists. Use -f to overwrite.' % filename)
                break

            out[filename] = open(filename, 'wb')
            atexit.register(out[filename].close)

        # Only write TMATS once.
        elif t == 0 and f == 1:
            continue

        # Handle special case for video data.
        if t == 8:
            data = b''.join([p.data for p in packet.body.mpeg])
        else:
            data = packet.body.data

        # Write out raw packet body.
        out[filename].write(data)

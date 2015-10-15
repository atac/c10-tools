#!/usr/bin/env python

"""
  copy.py - Copy all or part of a Chapter 10 file based on data types,
    channels, etc.

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

__doc__ = """usage: copy.py <src> <dst> [options]

Options:
    -c CHANNEL..., --channel CHANNEL...  Specify channels to include (csv).
    -e CHANNEL..., --exclude CHANNEL...  Specify channels to ignore (csv).
    -t TYPE, --type TYPE                 The types of data to copy (csv, may\
 be decimal or hex eg: 0x40)
    -f --force                           Overwrite existing files."""

import os

from chapter10 import C10
from docopt import docopt

from walk import walk_packets


if __name__ == '__main__':

    # Get commandline args.
    args = docopt(__doc__)

    # Don't overwrite unless explicitly required.
    if os.path.exists(args['<dst>']) and not args['--force']:
        print('dst file already exists. Use -f to overwrite.')
        raise SystemExit

    # Open input and output files.
    with open(args['<dst>'], 'wb') as out:
        src = C10(args['<src>'])

        # Iterate over packets based on args.
        for packet in walk_packets(src, args):

            # Copy packet to new file.
            raw = bytes(packet)
            if len(raw) == packet.packet_length:
                out.write(raw)

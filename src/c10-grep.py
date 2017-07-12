#!/usr/bin/env python

"""usage: c10-grep <value> <path>... [options]

Search Chapter 10 files/directories for "<value>" based on user input.

Options:
    -c CHANNEL, --channel CHANNEL  Channel ID
    --cmd CMDWORD                  1553 Command word
    -w WORD, --word-offset WORD    Word offset within message [default: 0]
    -m MASK, --mask=MASK           Value mask
"""

from datetime import timedelta
import os
import struct

from chapter10 import C10
from chapter10.datatypes.base import IterativeBase
from chapter10.datatypes import MS1553, Time
from docopt import docopt


def get_time(rtc, time_packet):
    """Get a datetime object based on last time packet and an RTC value."""

    time_packet.body.parse()
    t = time_packet.body.time
    offset = (rtc - time_packet.rtc) / 10000000
    t += timedelta(seconds=offset)
    return str(t)


def search(path, args):
    """Search file "path" based on parameters from "args"."""

    last_time = None
    for packet in C10(path, True):

        if isinstance(packet.body, Time):
            last_time = packet

        # Match channel
        if (args.get('--channel') or packet.channel_id) != packet.channel_id:
            continue

        # Iterate over messages if applicable
        if isinstance(packet.body, IterativeBase):
            packet.body.parse()

            for msg in packet.body:
                if isinstance(packet.body, MS1553):
                    cmd, = struct.unpack('=H', msg.data[:2])

                    # Match command word
                    if args.get('--cmd') and args.get('--cmd') != cmd:
                        continue

                    offset = args.get('--word-offset')
                    value, = struct.unpack('=H', msg.data[offset:offset + 2])

                    if args.get('--mask') is not None:
                        value &= args.get('--mask')

                    if value == args.get('<value>'):
                        print '    Found at %s' % get_time(
                            msg.intra_packet_timestamp, last_time)


if __name__ == '__main__':
    args = docopt(__doc__)

    # Validate int/hex inputs.
    for opt in ('--channel', '--word-offset', '--cmd', '<value>', '--mask'):
        if args.get(opt):
            try:
                if args[opt].lower().startswith('0x'):
                    args[opt] = int(args[opt], 16)
                else:
                    args[opt] = int(args[opt])
            except ValueError:
                print 'Invalid value "%s" for %s' % (args[opt], opt)
                raise SystemExit

    # Describe the search parameters.
    print 'Searching for %s' % hex(args.get('<value>')),
    if args.get('--channel'):
        print 'in channel #%s' % args.get('--channel'),
    if args.get('--cmd'):
        print 'with command word %s' % hex(args.get('--cmd')),
    if args.get('--word-offset'):
        print 'at word %s' % args.get('--word-offset'),
    if args.get('--mask'):
        print 'with mask %s' % hex(args.get('--mask')),
    print

    for path in args.get('<path>'):
        path = os.path.abspath(path)
        print 'Searching %s...' % path
        if os.path.isdir(path):
            for dirname, dirnames, filenames in os.walk(path):
                for f in filenames:

                    if os.path.splitext(f)[1] in ('.c10', '.ch10'):
                        f = os.path.join(dirname, f)
                        print '    %s...' % f[len(path) + 1:]
                        search(f, args)
        else:
            search(path, args)

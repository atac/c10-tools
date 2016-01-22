#!/usr/bin/env python

import os

from chapter10 import C10
from chapter10.datatypes import MS1553
from docopt import docopt
from tqdm import tqdm


error_keys = ('le', 'se', 'we')


def main(args):
    errcount = 0
    chan_errors = {}
    chan_count = {}
    file_size = os.stat(args['<file>']).st_size
    with tqdm(total=file_size, dynamic_ncols=True,
              unit='bytes', unit_scale=True, leave=True) as progress:
        if args['-q']:
            progress.close()
        for packet in C10(args['<file>']):
            if isinstance(packet.body, MS1553) and packet.body.format == 1:
                try:
                    chan_count[packet.channel_id] += 1
                except:
                    chan_count[packet.channel_id] = 1
                for msg in packet:
                    errors = [getattr(msg, k) for k in error_keys]
                    count = sum(errors)
                    if count:
                        errcount += count

                        try:
                            for i, err in enumerate(errors):
                                chan_errors[packet.channel_id][i] += err
                        except KeyError:
                            chan_errors[packet.channel_id] = errors
            if not args['-q']:
                try:
                    progress.update(packet.packet_length)
                except UnicodeEncodeError:
                    progress.ascii = True

    for label in ('Channel ID', 'Length', 'Sync', 'Word', 'Total', 'Packets'):
        print label.rjust(10),
    print
    print '-' * 80
    for k, v in sorted(chan_errors.items()):
        for cell in [k] + v:
            print str(cell).rjust(10),
        print str(sum(v)).rjust(10),
        print str(chan_count[k]).rjust(10)
    print '-' * 80
    print 'Totals:'.rjust(10),
    for i in range(len(error_keys)):
        print str(sum([chan[i] for chan in chan_errors.values()])).rjust(10),
    print str(errcount).rjust(10),
    print str(sum(chan_count.values())).rjust(10)


if __name__ == "__main__":
    args = docopt('''Counts error flags in 1553 format 1 packets
usage: c10-errcount <file> [-q]''')
    main(args)

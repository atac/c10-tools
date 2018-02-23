#!/usr/bin/env python

"""Counts error flags in 1553 format 1 packets
usage: 106errcount <file> [-q] [-l <logfile>]
"""

from __future__ import print_function
import sys
import os

from i106 import C10
from docopt import docopt
from tqdm import tqdm


error_keys = ('le', 'se', 'we')


def print_summary_labels(out=sys.stdout):
    for label in ('Channel ID', 'Length', 'Sync', 'Word', 'Total', 'Packets'):
        out.write(label.rjust(10) + ' ')
    out.write('\n')


def main(args):

    # Parse file.
    errcount = 0
    chan_errors = {}
    chan_count = {}
    file_size = os.stat(args['<file>']).st_size
    with tqdm(total=file_size, dynamic_ncols=True,
              unit='bytes', unit_scale=True, leave=True) as progress:
        if args['-q']:
            progress.leave = False
            progress.close()
        for packet in C10(args['<file>']):
            if packet.data_type == 25:
                try:
                    chan_count[packet.channel_id] += 1
                except KeyError:
                    chan_count[packet.channel_id] = 1
                valid = True
                for msg in packet:
                    errors = [getattr(msg, k) for k in error_keys]
                    count = sum(errors)
                    if count:
                        valid = False
                        errcount += count

                        try:
                            for i, err in enumerate(errors):
                                chan_errors[packet.channel_id][i] += err
                        except KeyError:
                            chan_errors[packet.channel_id] = errors
                if args['-l'] and not valid:
                    # Log to file
                    with open(args['<logfile>'], 'ab') as logfile:
                        for k in packet.HEADER_KEYS:
                            attr = '_'.join(k.split()).lower()
                            logfile.write('%s: %s\n'
                                          % (k, getattr(packet, attr)))
                        for label in ('Length', 'Sync', 'Word', 'Total'):
                            logfile.write(label.rjust(10) + ' ')
                        logfile.write('\n')
                        logfile.write('-' * 80)
                        logfile.write('\n')
                        for e in chan_errors[packet.channel_id]:
                            logfile.write(str(e).rjust(10) + ' ')
                        logfile.write(str(sum(
                            chan_errors[packet.channel_id])).rjust(10))
                        logfile.write('\n\n')
            if not args['-q']:
                try:
                    progress.update(packet.packet_length)
                except UnicodeEncodeError:
                    progress.ascii = True

    # Print summary.
    print_summary_labels()
    print ('-' * 80)
    for k, v in sorted(chan_errors.items()):
        for cell in [k] + v:
            print (str(cell).rjust(10), end=' ')
        print (str(sum(v)).rjust(10), end=' ')
        print (str(chan_count[k]).rjust(10))
    print ('-' * 80)
    print ('Totals:'.rjust(10), end=' ')
    for i in range(len(error_keys)):
        print (str(sum([chan[i] for chan in chan_errors.values()])).rjust(10),
               end=' ')
    print (str(errcount).rjust(10), end=' ')
    print (str(sum(chan_count.values())).rjust(10))


if __name__ == "__main__":
    args = docopt(__doc__)
    main(args)

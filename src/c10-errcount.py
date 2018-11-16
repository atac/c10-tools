#!/usr/bin/env python

"""Counts error flags in 1553 format 1 packets
usage: c10-errcount <file> [-q] [-l <logfile>]
"""

from __future__ import print_function
import csv
import os

from i106 import C10
from docopt import docopt
from tqdm import tqdm


error_keys = ('le', 'se', 'we')


def main(args):

    # Parse file.
    errcount = 0
    chan_errors = {}
    chan_count = {}
    file_size = os.stat(args['<file>']).st_size
    if args['-l']:
        with open(args['<logfile>'], 'w') as outfile:
            writer = csv.writer(outfile)
            writer.writerow(('Channel', 'Sequence', 'RTC', 'Length Errors',
                             'Sync Errors', 'Word Errors', 'Total Errors'))

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
                    with open(args['<logfile>'], 'a') as logfile:
                        writer = csv.writer(logfile)
                        row = []
                        for k in ('Channel ID', 'Sequence Number', 'RTC'):
                            attr = '_'.join(k.split()).lower()
                            row.append(getattr(packet, attr))
                        for e in chan_errors[packet.channel_id]:
                            row.append(str(e))

                        row.append(str(sum(chan_errors[packet.channel_id])))
                        writer.writerow(row)

            if not args['-q']:
                try:
                    progress.update(packet.packet_length)
                except UnicodeEncodeError:
                    progress.ascii = True

    # Print summary.
    for label in ('Channel ID', 'Length', 'Sync', 'Word', 'Total', 'Packets'):
        print(label.rjust(10), end=' ')
    print()
    print('-' * 80)
    for k, v in sorted(chan_errors.items()):
        for cell in [k] + v:
            print(str(cell).rjust(10), end=' ')
        print(str(sum(v)).rjust(10), end=' ')
        print(str(chan_count[k]).rjust(10))
    print('-' * 80)
    print('Totals:'.rjust(10), end=' ')
    for i in range(len(error_keys)):
        print(str(sum([chan[i] for chan in chan_errors.values()])).rjust(10),
              end=' ')
    print(str(errcount).rjust(10), end=' ')
    print(str(sum(chan_count.values())).rjust(10))


if __name__ == "__main__":
    args = docopt(__doc__)
    main(args)

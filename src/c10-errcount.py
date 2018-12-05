#!/usr/bin/env python

"""usage: c10-errcount <path>... [options]

Counts error flags in 1553 format 1 packets.

Options:
    -q            Quiet output (no progress bar)
    -o <logfile>  Output to CSV file with channel, sequence, and rtc
    -x            Run with multiprocessing (using dask)
"""

from __future__ import print_function
import csv
import os

try:
    from i106 import C10
except ImportError:
    from chapter10 import C10

from docopt import docopt
from tqdm import tqdm
from dask.delayed import delayed
import dask.bag as db

from common import find_c10


error_keys = ('le', 'se', 'we')


def parse_file(path, args):

    # Parse file.
    errcount = 0
    chan_errors = {}
    chan_count = {}
    file_size = os.stat(path).st_size

    with tqdm(total=file_size, dynamic_ncols=True,
              unit='bytes', unit_scale=True, leave=False) as progress:
        if args['-q']:
            progress.close()
        for packet in C10(path):
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
                if args['-o'] and not valid:
                    # Log to file
                    with open(args['-o'], 'a') as logfile:
                        writer = csv.writer(logfile, lineterminator='\n')
                        row = [path]
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
    print('=' * 80)
    print('File: ', path)
    print('=' * 80)
    for label in ('Channel ID', 'Length', 'Sync', 'Word', 'Total', 'Packets'):
        print(f'{label:>10}', end=' ')
    print()
    print('-' * 80)
    for k, v in sorted(chan_errors.items()):
        for cell in [k] + v:
            print(f'{cell:>10,}', end=' ')
        print(f'{sum(v):>10,}', end=' ')
        print(f'{chan_count[k]:>10,}')
    print('-' * 80)
    print('Totals:'.rjust(10), end=' ')
    for i in range(len(error_keys)):
        type_total = sum([chan[i] for chan in chan_errors.values()])
        print(f'{type_total:>10,}', end=' ')
    print(f'{errcount:>10,}', end=' ')
    print(f'{sum(chan_count.values()):>10,}')
    print()


if __name__ == "__main__":
    args = docopt(__doc__)
    if args['-o']:
        with open(args['-o'], 'w') as outfile:
            writer = csv.writer(outfile, lineterminator='\n')
            writer.writerow(('File', 'Channel', 'Sequence', 'RTC',
                             'Length Errors', 'Sync Errors', 'Word Errors',
                             'Total Errors'))
    files = find_c10(args['<path>'])
    if args.get('-x'):
        bag = db.from_delayed([delayed(parse_file)(path, args=args)
                               for path in files])
        bag.compute()
    else:
        for path in files:
            parse_file(path, args)

#!/usr/bin/env python

"""usage: c10-errcount <path>... [options]

Counts error flags in 1553 format 1 packets.

Options:
    -q            Quiet output (no progress bar)
    -o <logfile>  Output to CSV file with channel, sequence, and rtc
    -x            Run with multiprocessing (using dask)
"""

import csv
import sys

from docopt import docopt
from dask.delayed import delayed
import dask.bag as db

from c10_tools.common import find_c10, FileProgress, C10, fmt_table


error_keys = ('le', 'se', 'we')


def parse_file(path, args):

    # Parse file.
    errcount = 0
    chan_errors = {}
    chan_count = {}

    if not args['-q']:
        progress = FileProgress(path)

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
    print('File: ', path)
    table = [('Channel ID', 'Length', 'Sync', 'Word', 'Total', 'Packets')]
    for k, v in sorted(chan_errors.items()):
        row = [f'{cell:,}' for cell in [k] + v]
        row += [
            f'{sum(v):>,}',
            f'{chan_count[k]:>,}']
        table.append(row)

    footer = ['Totals:']
    for i in range(len(error_keys)):
        type_total = sum([chan[i] for chan in chan_errors.values()])
        footer.append(str(type_total))
    footer += [str(errcount), str(sum(chan_count.values()))]
    table.append(footer)

    print(fmt_table(table))


def main(args=sys.argv[1:]):
    args = docopt(__doc__, args)
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


if __name__ == "__main__":
    main()


from datetime import timedelta
import os

from docopt import docopt
from termcolor import colored

from c10_tools.common import FileProgress, C10


def wrapper():
    """usage: c10-timefix <input_file> <output_file>
    Ensure that time packets are at 1-second intervals.
    """

    print(colored('This will be deprecated in favor of c10 timefix', 'red'))
    args = docopt(wrapper.__doc__)
    for line in main(args):
        print(line)


def valid(timestamp, previous):
    """Validate a timestamp based on previous recorded one
    (should be at 1-second intervals).
    """

    if previous is None:
        return True

    diff = max(timestamp, previous) - min(timestamp, previous)
    return diff == timedelta(seconds=1)


def main(args):
    """Ensure that time packets are at 1-second intervals.
    timefix <input_file> <output_file> [options]
    -f, --force  Overwrite existing files.
    """

    if os.path.exists(args['<output_file>']) and not args['--force']:
        print('Output file exists. Use -f to overwrite.')
        raise SystemExit

    last_time = None
    with FileProgress(args['<input_file>'], disable=args['--quiet']) as progress, \
            open(args['<output_file>'], 'wb') as out_f:
        for packet in C10(args['<input_file>']):
            progress.update(packet.packet_length)

            if packet.data_type == 0x11:
                if not valid(packet.time, last_time):
                    packet.time = last_time + timedelta(seconds=1)
                last_time = packet.time

            out_f.write(bytes(packet))
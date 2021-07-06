
import csv
import sys

from chapter10 import C10


# TODO: file offset
KEYS = (
    'channel_id',
    'data_type',
    'sequence_number',
    'packet_length',
    'data_length',
    'header_version',
)

# TODO: selectable columns
# Pairs of (name, width)
COLUMNS = (
    ('Channel', 3),
    ('Type', 3),
    ('Sequence', 4),
    ('Size', 7),
    ('Version', 3),
    ('Time', 27),
    ('Version', 3),
)


# TODO: print ascii table to stdout or CSV to file (w/ progress bar)
# TODO: ensure that corrupted files can still be searched for valid packets
def main(args):
    """Report on packets found in a file.
    inspect <file>... [options]
    """
    
    writer = csv.writer(sys.stdout)
    keys = [k.replace('_', ' ').upper() for k in KEYS] + ['TIME', 'VALID']
    writer.writerow(keys)
    for f in args['<file>']:
        for packet in C10(f):
            row = [getattr(packet, a) for a in KEYS] + [packet.get_time(),
                                                        packet.validate(True)]
            writer.writerow(row)

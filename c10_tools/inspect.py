
from collections import OrderedDict
import csv
import os
import sys

from chapter10 import C10

from .common import fmt_number, FileProgress


class Inspect:
    KEYS = {
        'Channel': 'channel_id',
        'Type': 'data_type',
        'Sequence': 'sequence_number',
        'Size': 'packet_length',
    }

    # TODO: selectable columns
    # Pairs of (name, width)
    COLUMNS = OrderedDict((
        ('Channel', 7),
        ('Type', 4),
        ('Sequence', 8),
        ('Size', 7),
        ('Time', 27),
        ('Valid', 5),
        ('Offset', 15),
    ))
    
    def __init__(self, args):
        self.args = args
        self.cols = self.COLUMNS
        
        # Use CSV if stdout is redirected
        self.writer = None
        if os.fstat(0) != os.fstat(1):
            self.writer = csv.writer(sys.stdout, lineterminator='')
        
    def get_size(self):
        """Get total byte size for all files."""
        
        return sum(os.stat(f).st_size for f in self.args['<file>'])
        
    def write_header(self):
        """Write out header row for CSV or ASCII."""
        
        if self.writer:
            self.writer.writerow(self.cols.keys())
            return ''
            
        else:
            s = ' | '.join([f'{key:<{width}}'
                            for key, width in self.cols.items()])
            line = '-' * (len(s) + 4)
            return f'{line}\n| {s} |\n{line}'
        
    def write_row(self, packet, offset):
        """Pull values from a packet and write output row."""
        
        row = []
        for col, width in self.cols.items():
            if col == 'Time':
                row.append(str(packet.get_time()))
            elif col == 'Valid':
                row.append(packet.validate(True) and 'Yes' or 'No')
            elif col == 'Offset':
                row.append(fmt_number(offset).rjust(width))
            elif col in self.KEYS:
                val = getattr(packet, self.KEYS[col])
                if not self.writer:
                    val = fmt_number(val).rjust(width)
                row.append(val)

        s = ''
        if self.writer:
            self.writer.writerow(row)
            
        else:
            widths = list(self.cols.values())
            s = '|'
            for i, col in enumerate(row):
                s += f' {col:<{widths[i]}} |'

        return s

    # TODO: ensure that corrupted files can still be searched for valid packets
    def main(self):
        with FileProgress(total=self.get_size()) as progress:
            if self.args['--quiet'] or not self.writer:
                progress.close()

            header = self.write_header()
            yield header

            for f in self.args['<file>']:
                offset = 0
                for packet in C10(f):
                    progress.update(packet.packet_length)
                    yield self.write_row(packet, offset)
                    offset += packet.packet_length
        if header:
            yield header.split('\n', 1)[0]

def main(args):
    """Report on packets found in a file.
    inspect <file>... [options]
    """
    
    yield from Inspect(args).main()
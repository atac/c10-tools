
from collections import OrderedDict
import csv
import os
import sys

from chapter10 import C10

from .common import fmt_number, FileProgress


class Inspect:
    # TODO: file offset
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
    ))
    
    def __init__(self, args):
        self.args = args
        self.writer = None
        # Use CSV if stdout is redirected.
        if os.fstat(0) != os.fstat(1):
            self.writer = csv.writer(sys.stdout, lineterminator='')
        self.cols = self.COLUMNS
        
    def get_size(self):
        return sum(os.stat(f).st_size for f in self.args['<file>'])
        
    def write_header(self):
        if self.writer:
            self.writer.writerow(self.cols.keys())
            return ''
            
        else:
            s = ' | '.join([f'{key:<{width}}'
                            for key, width in self.cols.items()])
            line = '-' * (len(s) + 4)
            return f'{line}\n| {s} |\n{line}'
        
    def write_row(self, packet):
        row = []
        for col, width in self.cols.items():
            if col == 'Time':
                row.append(str(packet.get_time()))
            elif col == 'Valid':
                row.append(packet.validate(True) and 'Yes' or 'No')
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
        header = self.write_header()
        yield header
        with FileProgress(total=self.get_size()) as progress:
            if self.args['-q']:
                progress.close()
                
            for f in self.args['<file>']:
                for packet in C10(f):
                    progress.update(packet.packet_length)
                    yield self.write_row(packet)
        if header:
            yield header.split('\n', 1)[0]

def main(args):
    """Report on packets found in a file.
    inspect <file>... [options]
    """
    
    yield from Inspect(args).main()
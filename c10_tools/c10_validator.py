#!/usr/bin/env python


"""usage: c10-validator <file> [-q | -v] [options]

Options:
    -o FILE  Write valid data to a new file.
    -q       Don't show progress bar.
    -v       Print header details for every individual packet.
"""

import sys
import struct

from chapter10 import C10
from docopt import docopt

from c10_tools.common import FileProgress, fmt_number


class Parser:
    BUF_SIZE = 100000
    buf = b''

    def __init__(self, args=[]):
        self.args = docopt(__doc__, args)

    def main(self):
        valid, invalid = 0, 0
        with open(self.args['<file>'], 'rb') as f, \
                FileProgress(self.args['<file>']) as progress:

            while True:
                data = f.read(self.BUF_SIZE)
                progress.update(self.BUF_SIZE)
                if not data:
                    break

                self.buf = self.buf[-self.BUF_SIZE:] + data
                for i in range(self.buf.count(b'\x25\xeb')):

                    sync = self.buf.find(b'\x25\xeb')
                    if sync < 0:
                        break

                    try:
                        c10 = C10.from_string(self.buf[sync:])
                        packet = next(c10)

                        if packet.validate(True):
                            valid += 1

                            if self.args['-o']:
                                with open(self.args['-o'], 'ab') as out:
                                    out.write(bytes(packet))
                        else:
                            invalid += 1

                        if self.args['-v']:
                            print('(Valid)' if packet.check() else '(Invalid)')
                            print('''Sync: %(sync_pattern)s
    Channel ID: %(channel_id)s
    Packet Length: %(packet_length)s
    Data Length: %(data_length)s
    Header Version: %(header_version)s
    Sequence Number: %(sequence_number)s
    Flags: %(flags)s
    Data Type: %(data_type)s
    RTC: %(rtc)s
    Header Checksum: %(header_checksum)s
    ''' % packet.__dict__)
                    except (NotImplementedError, struct.error, OverflowError):
                        invalid += 1

        print('Found %s valid and %s invalid packets (total %s)' % (
            fmt_number(valid), fmt_number(invalid),
            fmt_number(valid + invalid)))


def main():
    Parser(sys.argv[1:]).main()


if __name__ == '__main__':
    main()

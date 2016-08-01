#!/usr/bin/env python


"""usage: c10-recovery <file> [-q | -v] [options]

Options:
-o FILE  Write valid data to a new file.
-q       Don't show progress bar.
-v       Print header details for every individual packet."""


import struct

from chapter10 import Packet
from docopt import docopt

from common import FileProgress, fmt_number

BUF_SIZE = 100000
buf = ''


def main():

    global buf

    args = docopt(__doc__)

    valid, invalid = 0, 0
    with open(args['<file>'], 'rb') as f, \
            FileProgress(args['<file>']) as progress:

        while True:
            data = f.read(BUF_SIZE)
            progress.update(BUF_SIZE)
            if not data:
                break

            buf = buf[-BUF_SIZE:] + data
            for i in range(buf.count('\x25\xeb')):

                sync = buf.find('\x25\xeb')
                if sync < 0:
                    break

                try:
                    packet = Packet.from_string(buf[sync:], True)
                    if packet.check():
                        valid += 1

                        if args['-o']:
                            with open(args['-o'], 'ab') as out:
                                out.write(bytes(packet))
                    else:
                        invalid += 1

                    if args['-v']:
                        print '(Valid)' if packet.check() else '(Invalid)'
                        print '''Sync: %(sync_pattern)s
Channel ID: %(channel_id)s
Packet Length: %(packet_length)s
Data Length: %(data_length)s
Header Version: %(header_version)s
Sequence Number: %(sequence_number)s
Flags: %(flags)s
Data Type: %(data_type)s
RTC: %(rtc)s
Header Checksum: %(header_checksum)s
''' % packet.__dict__
                except (NotImplementedError, struct.error, OverflowError):
                    invalid += 1

    print 'Found %s valid and %s invalid packets (total %s)' % (
        fmt_number(valid), fmt_number(invalid), fmt_number(valid + invalid))


if __name__ == '__main__':
    main()

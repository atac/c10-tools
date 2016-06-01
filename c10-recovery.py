#!/usr/bin/env python


"""usage: c10-recovery <file> [-q | -v] [options]

Options:
-o FILE  Write valid data to a new file.
-q       Don't show progress bar.
-v       Print header details for every individual packet."""


import os
import struct

from chapter10 import Packet
from docopt import docopt
from tqdm import tqdm

BUF_SIZE = 100000


def main():
    args = docopt(__doc__)

    valid, invalid = 0, 0
    buf = ''
    file_size = os.stat(args['<file>']).st_size
    with tqdm(total=file_size, dynamic_ncols=True,
              unit='bytes', unit_scale=True, leave=True) as progress, open(
                  args['<file>'], 'rb') as f:
        if args['-q']:
            progress.leave = False
            progress.close()
        run = True
        while run:
            read = f.read(BUF_SIZE)
            if len(read) < BUF_SIZE:
                run = False
            buf += read
            if not args['-q']:
                progress.update(len(read))

            sync = buf.find('\x25\xeb')
            if sync > -1:
                buf = buf[sync:]
                try:
                    packet = Packet.from_string(buf)
                    buf = buf[packet.packet_length:]
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
                except (NotImplementedError, struct.error):
                    invalid += 1

            buf = buf[-BUF_SIZE:]

    print 'Found %s valid and %s invalid packets (total %s)' % (
        valid, invalid, valid + invalid)


if __name__ == '__main__':
    main()

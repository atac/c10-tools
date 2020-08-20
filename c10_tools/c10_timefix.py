#!/usr/bin/env python

"""usage: c10-timefix <input_file> <output_file>

Check time packets within a chapter 10 file and ensure they are within an
acceptable offset of each other (5 seconds) or adjusts to 1 second offset.
"""

from datetime import timedelta
import struct
import sys

from docopt import docopt

from c10_tools.common import FileProgress, C10


def valid(timestamp, previous):
    """Validate a timestamp based on previous recorded one
    (within five seconds).
    """

    if previous is None:
        return True

    diff = max(timestamp, previous) - min(timestamp, previous)
    return diff < timedelta(seconds=5)


def main(args=sys.argv[1:]):

    args = docopt(__doc__, args)

    prev = None
    with open(args['<output_file>'], 'wb') as out_f, \
            FileProgress(args['<input_file>']) as progress:
        for packet in C10(args['<input_file>']):
            progress.update(packet.packet_length)
            raw = bytes(packet)
            if packet.data_type == 0x11:
                if valid(packet.time, prev):
                    out_f.write(raw)
                    prev = packet.time

                else:
                    # Manually write packet with new time.
                    time = prev + timedelta(seconds=1)
                    prev = time

                    # Write headers & csdw
                    prefix = 28
                    # if packet.secondary_sums:
                    #     prefix += 12
                    out_f.write(raw[:prefix])

                    # Time
                    TSn, Sn = (int(char) for char in str(time.second).zfill(2))
                    Hmn, Tmn = (int(char)
                                for char in str(time.microsecond).zfill(2)[:2])
                    TMn, Mn = (int(char) for char in str(time.minute).zfill(2))
                    THn, Hn = (int(char) for char in str(time.hour).zfill(2))
                    data = [
                        (TSn << 12) + (Sn << 8) + (Hmn << 4) + Tmn,
                        (THn << 12) + (Hn << 8) + (TMn << 4) + Mn,
                    ]

                    # IRIG day
                    if not packet.body.date_fmt:
                        day = time.timetuple().tm_yday
                        HDn, TDn, Dn = (int(char) for char in str(day))

                        data.append((HDn << 8) + (TDn << 4) + Dn)

                    # Month and year
                    else:
                        TOn, On = (
                            int(char) for char in str(time.month).zfill(2))
                        TDn, Dn = (
                            int(char) for char in str(time.day).zfill(2))
                        OYn, HYn, TYn, Yn = (
                            int(char) for char in str(time.year))

                        data.append((TOn << 12) + (On << 8) + (TDn << 4) + Dn)
                        data.append((OYn << 12) + (HYn << 8) + (TYn << 4) + Yn)

                    out_f.write(struct.pack('H' * len(data), *data))

            else:
                # Write packet to file
                out_f.write(raw)


if __name__ == "__main__":
    main()

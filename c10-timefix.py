#!/usr/bin/env python

from datetime import timedelta
import struct
import sys

from chapter10 import C10
from chapter10.datatypes import Time


def valid(timestamp, previous):
    """Validate a timestamp based on previous recorded one
    (within five seconds).
    """

    if previous is None:
        return True

    if timestamp > previous:
        diff = timestamp - previous
    else:
        diff = previous - timestamp
    if diff > timedelta(seconds=5):
        return False
    return True


def main():

    if len(sys.argv) < 2:
        print 'usage: timefix <input_file> <output_file>'

    prev = None
    with open(sys.argv[-1], 'wb') as out_f:
        for packet in C10(sys.argv[-2]):
            if isinstance(packet.body, Time):
                if valid(packet.body.time, prev):
                    out_f.write(bytes(packet))
                    prev = packet.body.time

                else:
                    # Manually write packet with new time.
                    time = prev + timedelta(seconds=1)
                    prev = time

                    # Write headers & csdw
                    prefix = 28
                    if packet.secondary_sums:
                        prefix += 12
                    raw = bytes(packet)
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

                print prev

            else:
                # Write packet to file
                out_f.write(bytes(packet))


if __name__ == "__main__":
    main()

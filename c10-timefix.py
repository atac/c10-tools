#!/usr/bin/env python

"""
  c10-timefix.py - Copy a chapter 10 file and rebuild time packets if needed.

 Copyright (c) 2015 Micah Ferrill

 All rights reserved.

 Redistribution and use in source and binary forms, with or without
 modification, are permitted provided that the following conditions are
 met:

   * Redistributions of source code must retain the above copyright
     notice, this list of conditions and the following disclaimer.

   * Redistributions in binary form must reproduce the above copyright
     notice, this list of conditions and the following disclaimer in the
     documentation and/or other materials provided with the distribution.

   * Neither the name Irig106.org nor the names of its contributors may
     be used to endorse or promote products derived from this software
     without specific prior written permission.

 This software is provided by the copyright holders and contributors
 "as is" and any express or implied warranties, including, but not
 limited to, the implied warranties of merchantability and fitness for
 a particular purpose are disclaimed. In no event shall the copyright
 owner or contributors be liable for any direct, indirect, incidental,
 special, exemplary, or consequential damages (including, but not
 limited to, procurement of substitute goods or services; loss of use,
 data, or profits; or business interruption) however caused and on any
 theory of liability, whether in contract, strict liability, or tort
 (including negligence or otherwise) arising in any way out of the use
 of this software, even if advised of the possibility of such damage.
"""

__doc__ = 'usage: c10-timefix <input_file> <output_file>'

from datetime import timedelta
import struct

from chapter10 import C10
from chapter10.datatypes import Time
from docopt import docopt


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

    args = docopt(__doc__)

    prev = None
    with open(args['<output_file>'], 'wb') as out_f:
        for packet in C10(args['<input_file>']):
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

            else:
                # Write packet to file
                out_f.write(bytes(packet))


if __name__ == "__main__":
    main()
